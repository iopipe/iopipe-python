from botocore.httpsession import URLLib3Session as BotocoreSession
from botocore.vendored.requests.sessions import Session as BotocoreVendoredSession
from requests.sessions import Session as RequestsSession

from iopipe.contrib.trace.auto_http import patch_requests, restore_requests


def test_monkey_patching(mock_context):
    assert not hasattr(RequestsSession.send, "monkey_patched")
    assert not hasattr(BotocoreSession.send, "monkey_patched")
    assert not hasattr(BotocoreVendoredSession.send, "monkey_patched")

    patch_requests(mock_context, None)

    assert hasattr(RequestsSession.send, "monkey_patched")
    assert hasattr(BotocoreSession.send, "monkey_patched")
    assert hasattr(BotocoreVendoredSession.send, "monkey_patched")

    restore_requests()

    assert not hasattr(RequestsSession.send, "monkey_patched")
    assert not hasattr(BotocoreSession.send, "monkey_patched")
    assert not hasattr(BotocoreVendoredSession.send, "monkey_patched")
