from stripe.api_resources.abstract import CreateableAPIResource
from stripe.api_resources.abstract import DeletableAPIResource
from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class Recipient(
    CreateableAPIResource,
    UpdateableAPIResource,
    ListableAPIResource,
    DeletableAPIResource,
):
    OBJECT_NAME = "recipient"
