from stripe import api_requestor, util
from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class Charge(
    CreateableAPIResource, ListableAPIResource, UpdateableAPIResource
):
    OBJECT_NAME = "charge"

    async def refund(self, idempotency_key=None, **params):
        url = self.instance_url() + "/refund"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def capture(self, idempotency_key=None, **params):
        url = self.instance_url() + "/capture"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def update_dispute(self, idempotency_key=None, **params):
        requestor = api_requestor.APIRequestor(
            self.api_key,
            api_version=self.stripe_version,
            account=self.stripe_account,
        )
        url = self.instance_url() + "/dispute"
        headers = util.populate_headers(idempotency_key)
        response, api_key = await requestor.request("post", url, params, headers)
        self.refresh_from({"dispute": response}, api_key, True)
        return self.dispute

    async def close_dispute(self, idempotency_key=None, **params):
        requestor = api_requestor.APIRequestor(
            self.api_key,
            api_version=self.stripe_version,
            account=self.stripe_account,
        )
        url = self.instance_url() + "/dispute/close"
        headers = util.populate_headers(idempotency_key)
        response, api_key = await requestor.request("post", url, params, headers)
        self.refresh_from({"dispute": response}, api_key, True)
        return self.dispute

    async def mark_as_fraudulent(self, idempotency_key=None):
        params = {"fraud_details": {"user_report": "fraudulent"}}
        url = self.instance_url()
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def mark_as_safe(self, idempotency_key=None):
        params = {"fraud_details": {"user_report": "safe"}}
        url = self.instance_url()
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self
