from botocore.httpsession import URLLib3Session as BotocoreSession
from botocore.vendored.requests.sessions import Session as BotocoreVendoredSession
from requests.sessions import Session as RequestsSession

from iopipe.contrib.trace.auto_http import patch_requests, restore_requests


def test_monkey_patching(mock_context):
    assert not hasattr(RequestsSession, "__monkey_patched")
    assert not hasattr(BotocoreSession, "__monkey_patched")
    assert not hasattr(BotocoreVendoredSession, "__monkey_patched")

    def mock_filter(request, response):
        return request, response

    patch_requests(mock_context, mock_filter)

    assert hasattr(RequestsSession, "__monkey_patched")
    assert hasattr(BotocoreSession, "__monkey_patched")
    assert hasattr(BotocoreVendoredSession, "__monkey_patched")

    restore_requests()

    assert not hasattr(RequestsSession, "__monkey_patched")
    assert not hasattr(BotocoreSession, "__monkey_patched")
    assert not hasattr(BotocoreVendoredSession, "__monkey_patched")
