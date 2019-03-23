from stripe import api_requestor
from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import DeletableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class Subscription(
    CreateableAPIResource,
    DeletableAPIResource,
    UpdateableAPIResource,
    ListableAPIResource,
):
    OBJECT_NAME = "subscription"

    async def delete_discount(self, **params):
        requestor = api_requestor.APIRequestor(
            self.api_key,
            api_version=self.stripe_version,
            account=self.stripe_account,
        )
        url = self.instance_url() + "/discount"
        _, api_key = await requestor.request("delete", url, params)
        self.refresh_from({"discount": None}, api_key, True)
