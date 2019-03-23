from stripe import util


class VerifyMixin(object):
    async def verify(self, idempotency_key=None, **params):
        url = self.instance_url() + "/verify"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self
