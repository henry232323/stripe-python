from stripe import util
from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource


class PaymentMethod(
    CreateableAPIResource, ListableAPIResource, UpdateableAPIResource
):
    OBJECT_NAME = "payment_method"

    async def attach(self, idempotency_key=None, **params):
        url = self.instance_url() + "/attach"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def detach(self, idempotency_key=None, **params):
        url = self.instance_url() + "/detach"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self
