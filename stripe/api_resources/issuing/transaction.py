from stripe.api_resources.abstract import UpdateableAPIResource
from stripe.api_resources.abstract import ListableAPIResource


class Transaction(ListableAPIResource, UpdateableAPIResource):
    OBJECT_NAME = "issuing.transaction"
