from stripe import util
from stripe.stripe_object import StripeObject

from urllib.parse import quote_plus


class ListObject(StripeObject):
    OBJECT_NAME = "list"

    async def list(self, **params):
        return await self.request("get", self["url"], params)

    async def auto_paging_iter(self):
        page = self
        params = dict(self._retrieve_params)

        while True:
            item_id = None
            for item in page:
                item_id = item.get("id", None)
                yield item

            if not getattr(page, "has_more", False) or item_id is None:
                return

            params["starting_after"] = item_id
            page = await self.list(**params)

    async def create(self, idempotency_key=None, **params):
        headers = util.populate_headers(idempotency_key)
        return await self.request("post", self["url"], params, headers)

    async def retrieve(self, id, **params):
        base = self.get("url")
        id = util.utf8(id)
        extn = quote_plus(id)
        url = "%s/%s" % (base, extn)

        return await self.request("get", url, params)

    def __iter__(self):
        return getattr(self, "data", []).__iter__()

    def __len__(self):
        return getattr(self, "data", []).__len__()
