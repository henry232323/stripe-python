from stripe import util
from stripe.api_resources import ApplicationFee
from stripe.api_resources.abstract import UpdateableAPIResource

from urllib.parse import quote_plus


class ApplicationFeeRefund(UpdateableAPIResource):
    OBJECT_NAME = "fee_refund"

    @classmethod
    def _build_instance_url(cls, fee, sid):
        fee = util.utf8(fee)
        sid = util.utf8(sid)
        base = ApplicationFee.class_url()
        cust_extn = quote_plus(fee)
        extn = quote_plus(sid)
        return "%s/%s/refunds/%s" % (base, cust_extn, extn)

    @classmethod
    async def modify(cls, fee, sid, **params):
        url = cls._build_instance_url(fee, sid)
        return await cls._modify(url, **params)

    def instance_url(self):
        return self._build_instance_url(self.fee, self.id)

    @classmethod
    def retrieve(cls, id, api_key=None, **params):
        raise NotImplementedError(
            "Can't retrieve a refund without an application fee ID. "
            "Use application_fee.refunds.retrieve('refund_id') instead."
        )
