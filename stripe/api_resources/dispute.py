from stripe import util
from stripe.api_resources.abstract import ListableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource


class Dispute(ListableAPIResource, UpdateableAPIResource):
    OBJECT_NAME = "dispute"

    async def close(self, idempotency_key=None, **params):
        url = self.instance_url() + "/close"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self
