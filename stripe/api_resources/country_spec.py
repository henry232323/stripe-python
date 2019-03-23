from stripe.api_resources import abstract


class CountrySpec(abstract.ListableAPIResource):
    OBJECT_NAME = "country_spec"
