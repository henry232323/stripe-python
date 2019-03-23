from stripe import api_requestor, util
from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import DeletableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class Invoice(
    CreateableAPIResource,
    UpdateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
):
    OBJECT_NAME = "invoice"

    async def finalize_invoice(self, idempotency_key=None, **params):
        url = self.instance_url() + "/finalize"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def mark_uncollectible(self, idempotency_key=None, **params):
        url = self.instance_url() + "/mark_uncollectible"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def pay(self, idempotency_key=None, **params):
        url = self.instance_url() + "/pay"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def send_invoice(self, idempotency_key=None, **params):
        url = self.instance_url() + "/send"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    @classmethod
    async def upcoming(
        cls, api_key=None, stripe_version=None, stripe_account=None, **params
    ):
        requestor = api_requestor.APIRequestor(
            api_key, api_version=stripe_version, account=stripe_account
        )
        url = cls.class_url() + "/upcoming"
        response, api_key = await requestor.request("get", url, params)
        return util.convert_to_stripe_object(
            response, api_key, stripe_version, stripe_account
        )

    async def void_invoice(self, idempotency_key=None, **params):
        url = self.instance_url() + "/void"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self
