from botocore.awsrequest import AWSRequest
from botocore.httpsession import URLLib3Session as BotocoreSession
from botocore.vendored.requests.sessions import (
    PreparedRequest,
    Session as BotocoreVendoredSession,
)
from requests.sessions import Session as RequestsSession

from iopipe.contrib.trace.auto_http import patch_http_requests, restore_http_requests


def test_patch_http_requests(mock_context_wrapper,):
    assert not hasattr(BotocoreSession.send, "__wrapped__")
    assert not hasattr(BotocoreVendoredSession.send, "__wrapped__")
    assert not hasattr(RequestsSession.send, "__wrapped__")

    def mock_filter(request, response):
        return request, response

    http_headers = ["Cache-Control"]

    patch_http_requests(mock_context_wrapper, mock_filter, http_headers)

    assert hasattr(BotocoreSession.send, "__wrapped__")
    assert hasattr(BotocoreVendoredSession.send, "__wrapped__")
    assert hasattr(RequestsSession.send, "__wrapped__")

    restore_http_requests()

    assert not hasattr(BotocoreSession.send, "__wrapped__")
    assert not hasattr(BotocoreVendoredSession.send, "__wrapped__")
    assert not hasattr(RequestsSession.send, "__wrapped__")


def test_patch_http_requests_no_iopipe(mock_context,):
    """Asserts that monkey patching does not occur if IOpipe not present"""
    restore_http_requests()

    assert not hasattr(BotocoreSession.send, "__wrapped__")
    assert not hasattr(BotocoreVendoredSession.send, "__wrapped__")
    assert not hasattr(RequestsSession.send, "__wrapped__")

    delattr(mock_context, "iopipe")

    patch_http_requests(mock_context, None, None)

    assert not hasattr(BotocoreSession.send, "__wrapped__")
    assert not hasattr(BotocoreVendoredSession.send, "__wrapped__")
    assert not hasattr(RequestsSession.send, "__wrapped__")


def test_patch_http_requests_send(mock_context_wrapper):
    patch_http_requests(mock_context_wrapper, None, None)

    assert hasattr(BotocoreSession.send, "__wrapped__")
    assert hasattr(BotocoreVendoredSession.send, "__wrapped__")

    botocore_session = BotocoreSession()
    botocore_session.send(AWSRequest(method="GET", url="https://www.iopipe.com"))

    botocore_vendored_session = BotocoreVendoredSession()
    request = PreparedRequest()
    request.prepare(method="GET", url="https://www.iopipe.com")
    botocore_vendored_session.send(request)
