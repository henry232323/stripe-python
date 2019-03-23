from stripe import util
from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class PaymentIntent(
    CreateableAPIResource, UpdateableAPIResource, ListableAPIResource
):
    OBJECT_NAME = "payment_intent"

    async def cancel(self, idempotency_key=None, **params):
        url = self.instance_url() + "/cancel"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def capture(self, idempotency_key=None, **params):
        url = self.instance_url() + "/capture"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def confirm(self, idempotency_key=None, **params):
        url = self.instance_url() + "/confirm"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self
