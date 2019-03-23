from stripe.api_resources.abstract.api_resource import APIResource


class DeletableAPIResource(APIResource):
    async def delete(self, **params):
        self.refresh_from(await self.request("delete", self.instance_url(), params))
        return self
