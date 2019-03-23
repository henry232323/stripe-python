from stripe import util
from stripe.api_resources.abstract import ListableAPIResource


class Review(ListableAPIResource):
    OBJECT_NAME = "review"

    async def approve(self, idempotency_key=None, **params):
        url = self.instance_url() + "/approve"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self
