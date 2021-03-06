from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import DeletableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class SubscriptionItem(
    CreateableAPIResource,
    DeletableAPIResource,
    UpdateableAPIResource,
    ListableAPIResource,
):
    OBJECT_NAME = "subscription_item"

    async def usage_record_summaries(self, **params):
        return await self.request(
            "get", self.instance_url() + "/usage_record_summaries", params
        )
