from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class Card(CreateableAPIResource, ListableAPIResource, UpdateableAPIResource):
    OBJECT_NAME = "issuing.card"

    async def details(self, idempotency_key=None, **params):
        return await self.request("get", self.instance_url() + "/details", params)
