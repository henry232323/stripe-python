import sys
import textwrap
import warnings
import email
import time
import random
import threading
import json
import asyncio

import stripe
from stripe import error, util
from stripe.request_metrics import RequestMetrics

# - Requests is the preferred HTTP library
# - Google App Engine has urlfetch
# - Use Pycurl if it's there (at least it verifies SSL certs)
# - Fall back to urllib2 with a warning if needed

import aiohttp

# proxy support for the pycurl client
from urllib.parse import urlparse


def _now_ms():
    return int(round(time.time() * 1000))


def new_default_http_client(*args, **kwargs):
    impl = AIOHTTPClient

    return impl(*args, **kwargs)


class HTTPClient(object):
    MAX_DELAY = 2
    INITIAL_DELAY = 0.5

    def __init__(self, verify_ssl_certs=True, proxy=None):
        self._verify_ssl_certs = verify_ssl_certs
        if proxy:
            if type(proxy) is str:
                proxy = {"http": proxy, "https": proxy}
            if not (type(proxy) is dict):
                raise ValueError(
                    "Proxy(ies) must be specified as either a string "
                    "URL or a dict() with string URL under the"
                    " "
                    "https"
                    " and/or "
                    "http"
                    " keys."
                )
        self._proxy = proxy.copy() if proxy else None

        self._thread_local = threading.local()

    async def request_with_retries(self, method, url, headers, post_data=None):
        self._add_telemetry_header(headers)

        num_retries = 0

        while True:
            request_start = _now_ms()

            try:
                num_retries += 1
                response = await self.request(method, url, headers, post_data)
                connection_error = None
            except error.APIConnectionError as e:
                connection_error = e
                response = None

            if self._should_retry(response, connection_error, num_retries):
                if connection_error:
                    util.log_info(
                        "Encountered a retryable error %s"
                        % connection_error.user_message
                    )

                sleep_time = self._sleep_time_seconds(num_retries)
                util.log_info(
                    (
                        "Initiating retry %i for request %s %s after "
                        "sleeping %.2f seconds."
                        % (num_retries, method, url, sleep_time)
                    )
                )
                time.sleep(sleep_time)
            else:
                if response is not None:
                    self._record_request_metrics(response, request_start)

                    return response
                else:
                    raise connection_error

    async def request(self, method, url, headers, post_data=None):
        raise NotImplementedError(
            "HTTPClient subclasses must implement `request`"
        )

    def _should_retry(self, response, api_connection_error, num_retries):
        if response is not None:
            _, status_code, _ = response
            should_retry = status_code == 409
        else:
            # We generally want to retry on timeout and connection
            # exceptions, but defer this decision to underlying subclass
            # implementations. They should evaluate the driver-specific
            # errors worthy of retries, and set flag on the error returned.
            should_retry = api_connection_error.should_retry
        return should_retry and num_retries < self._max_network_retries()

    def _max_network_retries(self):
        from stripe import max_network_retries

        # Configured retries, isolated here for tests
        return max_network_retries

    def _sleep_time_seconds(self, num_retries):
        # Apply exponential backoff with initial_network_retry_delay on the
        # number of num_retries so far as inputs.
        # Do not allow the number to exceed max_network_retry_delay.
        sleep_seconds = min(
            HTTPClient.INITIAL_DELAY * (2 ** (num_retries - 1)),
            HTTPClient.MAX_DELAY,
        )

        sleep_seconds = self._add_jitter_time(sleep_seconds)

        # But never sleep less than the base sleep seconds.
        sleep_seconds = max(HTTPClient.INITIAL_DELAY, sleep_seconds)
        return sleep_seconds

    def _add_jitter_time(self, sleep_seconds):
        # Randomize the value in [(sleep_seconds/ 2) to (sleep_seconds)]
        # Also separated method here to isolate randomness for tests
        sleep_seconds *= 0.5 * (1 + random.uniform(0, 1))
        return sleep_seconds

    def _add_telemetry_header(self, headers):
        last_request_metrics = getattr(
            self._thread_local, "last_request_metrics", None
        )
        if stripe.enable_telemetry and last_request_metrics:
            telemetry = {
                "last_request_metrics": last_request_metrics.payload()
            }
            headers["X-Stripe-Client-Telemetry"] = json.dumps(telemetry)

    def _record_request_metrics(self, response, request_start):
        _, _, rheaders = response
        if "Request-Id" in rheaders and stripe.enable_telemetry:
            request_id = rheaders["Request-Id"]
            request_duration_ms = _now_ms() - request_start
            self._thread_local.last_request_metrics = RequestMetrics(
                request_id, request_duration_ms
            )

    async def close(self):
        raise NotImplementedError(
            "HTTPClient subclasses must implement `close`"
        )


class AIOHTTPClient(HTTPClient):
    name = "requests"

    def __init__(self, timeout=80, session=None, loop=None, **kwargs):
        super(AIOHTTPClient, self).__init__(**kwargs)
        self._session = session
        self._timeout = timeout
        self.loop = loop
        if loop is None:
            self.loop = asyncio.get_event_loop()

    async def request(self, method, url, headers, post_data=None):
        kwargs = {}
        if self._verify_ssl_certs:
            kwargs["verify"] = stripe.ca_bundle_path
        else:
            kwargs["verify"] = False

        if self._proxy:
            kwargs["proxies"] = self._proxy

        if getattr(self._thread_local, "session", None) is None:
            self._thread_local.session = self._session or aiohttp.ClientSession(loop=self.loop)

        try:
            try:
                result = await self._thread_local.session.request(
                    method,
                    url,
                    headers=headers,
                    data=post_data,
                    timeout=self._timeout,
                    **kwargs
                )
            except TypeError as e:
                raise TypeError(
                    "Warning: It looks like your installed version of the "
                    '"requests" library is not compatible with Stripe\'s '
                    "usage thereof. (HINT: The most likely cause is that "
                    'your "requests" library is out of date. You can fix '
                    'that by running "pip install -U requests".) The '
                    "underlying error was: %s" % (e,)
                )

            # This causes the content to actually be read, which could cause
            # e.g. a socket timeout. TODO: The other fetch methods probably
            # are susceptible to the same and should be updated.
            content = result.content
            status_code = result.status_code
        except Exception as e:
            # Would catch just requests.exceptions.RequestException, but can
            # also raise ValueError, RuntimeError, etc.
            self._handle_request_error(e)
        return content, status_code, result.headers

    def _handle_request_error(self, e):

        # Catch SSL error first as it belongs to ConnectionError,
        # but we don't want to retry
        if isinstance(e, aiohttp.ClientSSLError):
            msg = (
                "Could not verify Stripe's SSL certificate.  Please make "
                "sure that your network is not intercepting certificates.  "
                "If this problem persists, let us know at "
                "support@stripe.com."
            )
            err = "%s: %s" % (type(e).__name__, str(e))
            should_retry = False
        # Retry only timeout and connect errors; similar to urllib3 Retry
        elif isinstance(e, aiohttp.ServerTimeoutError) or isinstance(
            e, aiohttp.ClientConnectionError
        ):
            msg = (
                "Unexpected error communicating with Stripe.  "
                "If this problem persists, let us know at "
                "support@stripe.com."
            )
            err = "%s: %s" % (type(e).__name__, str(e))
            should_retry = True
        # Catch remaining request exceptions
        elif isinstance(e, aiohttp.ClientError):
            msg = (
                "Unexpected error communicating with Stripe.  "
                "If this problem persists, let us know at "
                "support@stripe.com."
            )
            err = "%s: %s" % (type(e).__name__, str(e))
            should_retry = False
        else:
            msg = (
                "Unexpected error communicating with Stripe. "
                "It looks like there's probably a configuration "
                "issue locally.  If this problem persists, let us "
                "know at support@stripe.com."
            )
            err = "A %s was raised" % (type(e).__name__,)
            if str(e):
                err += " with error message %s" % (str(e),)
            else:
                err += " with no error message"
            should_retry = False

        msg = textwrap.fill(msg) + "\n\n(Network error: %s)" % (err,)
        raise error.APIConnectionError(msg, should_retry=should_retry)

    def close(self):
        if getattr(self._thread_local, "session", None) is not None:
            self._thread_local.session.close()
