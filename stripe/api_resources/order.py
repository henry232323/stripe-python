from stripe import util
from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class Order(CreateableAPIResource, UpdateableAPIResource, ListableAPIResource):
    OBJECT_NAME = "order"

    async def pay(self, idempotency_key=None, **params):
        url = self.instance_url() + "/pay"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def return_order(self, idempotency_key=None, **params):
        headers = util.populate_headers(idempotency_key)
        return await self.request(
            "post", self.instance_url() + "/returns", params, headers
        )
