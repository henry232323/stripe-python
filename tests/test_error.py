# -*- coding: utf-8 -*-

from stripe import six, error


class TestStripeError(object):
    def test_formatting(self):
        err = error.StripeError(u"öre")
        assert str(err) == u"öre"
        if six.PY2:
            assert str(err) == "\xc3\xb6re"
        else:
            assert str(err) == u"öre"

    def test_formatting_with_request_id(self):
        err = error.StripeError(u"öre", headers={"request-id": "123"})
        assert str(err) == u"Request 123: öre"
        if six.PY2:
            assert str(err) == "Request 123: \xc3\xb6re"
        else:
            assert str(err) == u"Request 123: öre"

    def test_formatting_with_none(self):
        err = error.StripeError(None, headers={"request-id": "123"})
        assert str(err) == u"Request 123: <empty message>"
        if six.PY2:
            assert str(err) == "Request 123: <empty message>"
        else:
            assert str(err) == "Request 123: <empty message>"

    def test_formatting_with_message_none_and_request_id_none(self):
        err = error.StripeError(None)
        assert str(err) == u"<empty message>"
        if six.PY2:
            assert str(err) == "<empty message>"
        else:
            assert str(err) == u"<empty message>"

    def test_repr(self):
        err = error.StripeError(u"öre", headers={"request-id": "123"})
        if six.PY2:
            assert (
                repr(err)
                == "StripeError(message=u'\\xf6re', http_status=None, "
                "request_id='123')"
            )
        else:
            assert (
                repr(err) == "StripeError(message='öre', http_status=None, "
                "request_id='123')"
            )


class TestStripeErrorWithParamCode(object):
    def test_repr(self):
        err = error.CardError(
            u"öre",
            param="cparam",
            code="ccode",
            http_status=403,
            headers={"request-id": "123"},
        )
        if six.PY2:
            assert (
                repr(err) == "CardError(message=u'\\xf6re', param='cparam', "
                "code='ccode', http_status=403, request_id='123')"
            )
        else:
            assert (
                repr(err)
                == "CardError(message='öre', param='cparam', code='ccode', "
                "http_status=403, request_id='123')"
            )


class TestApiConnectionError(object):
    def test_default_no_retry(self):
        err = error.APIConnectionError("msg")
        assert err.should_retry is False

        err = error.APIConnectionError("msg", should_retry=True)
        assert err.should_retry
