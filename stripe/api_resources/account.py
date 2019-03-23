import stripe
from stripe import oauth, util
from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import DeletableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource
from stripe.api_resources.abstract import nested_resource_class_methods

from urllib.parse import quote_plus


@nested_resource_class_methods(
    "external_account",
    operations=["create", "retrieve", "update", "delete", "list"],
)
@nested_resource_class_methods("login_link", operations=["create"])
@nested_resource_class_methods(
    "person", operations=["create", "retrieve", "update", "delete", "list"]
)
class Account(
    CreateableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
    DeletableAPIResource,
):
    OBJECT_NAME = "account"

    @classmethod
    def retrieve(cls, id=None, api_key=None, **params):
        instance = cls(id, api_key, **params)
        instance.refresh()
        return instance

    @classmethod
    async def modify(cls, id=None, **params):
        return await cls._modify(cls._build_instance_url(id), **params)

    @classmethod
    def _build_instance_url(cls, sid):
        if not sid:
            return "/v1/account"
        sid = util.utf8(sid)
        base = cls.class_url()
        extn = quote_plus(sid)
        return "%s/%s" % (base, extn)

    def instance_url(self):
        return self._build_instance_url(self.get("id"))

    async def persons(self, **params):
        return await self.request("get", self.instance_url() + "/persons", params)

    async def reject(self, idempotency_key=None, **params):
        url = self.instance_url() + "/reject"
        headers = util.populate_headers(idempotency_key)
        self.refresh_from(await self.request("post", url, params, headers))
        return self

    async def deauthorize(self, **params):
        params["stripe_user_id"] = self.id
        return await oauth.OAuth.deauthorize(**params)

    async def serialize(self, previous):
        params = super(Account, self).serialize(previous)
        previous = previous or self._previous or {}

        for k, v in iter(self.items()):
            if (
                k == "individual"
                and isinstance(v, stripe.api_resources.Person)
                and k not in params
            ):
                params[k] = v.serialize(previous.get(k, None))

        return params
