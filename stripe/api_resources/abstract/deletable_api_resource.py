from __future__ import absolute_import, division, print_function

from stripe import api_requestor, util
from stripe.api_resources.abstract.api_resource import APIResource
from stripe.six.moves.urllib.parse import quote_plus


class DeletableAPIResource(APIResource):
    @classmethod
    def _delete(
        cls,
        url,
        api_key=None,
        idempotency_key=None,
        stripe_version=None,
        stripe_account=None,
        **params
    ):
        requestor = api_requestor.APIRequestor(
            api_key, api_version=stripe_version, account=stripe_account
        )
        headers = util.populate_headers(idempotency_key)
        response, api_key = requestor.request("delete", url, params, headers)
        return util.convert_to_stripe_object(
            response, api_key, stripe_version, stripe_account
        )

    @util.class_or_instance_method
    def delete(cls_or_self, *args, **kwargs):
        if isinstance(cls_or_self, type):
            cls = cls_or_self
            sid = args[0]
            url = "%s/%s" % (cls.class_url(), quote_plus(util.utf8(sid)))
            return cls._delete(url, **kwargs)
            return None
        else:
            self = cls_or_self
            self.refresh_from(
                self.request("delete", self.instance_url(), kwargs)
            )
            return self
