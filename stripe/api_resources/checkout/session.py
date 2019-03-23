from stripe.api_resources.abstract import CreateableAPIResource


class Session(CreateableAPIResource):
    OBJECT_NAME = "checkout.session"
