import mock

from botocore.httpsession import URLLib3Session as BotocoreSession
from botocore.vendored.requests.sessions import Session as BotocoreVendoredSession
from requests.sessions import Session as RequestsSession

from iopipe.contrib.trace.auto_http import patch_http_requests, restore_http_requests


@mock.patch("iopipe.contrib.trace.auto_http.original_requests_session_send")
@mock.patch("iopipe.contrib.trace.auto_http.original_botocore_session_send")
@mock.patch("iopipe.contrib.trace.auto_http.original_botocore_vendored_session_send")
def test_monkey_patching(
    mock_botocore_vendored_session_send,
    mock_botocore_session_send,
    mock_requests_session_send,
    mock_context_wrapper,
):
    assert not hasattr(RequestsSession, "__monkey_patched")
    assert not hasattr(BotocoreSession, "__monkey_patched")
    assert not hasattr(BotocoreVendoredSession, "__monkey_patched")

    def mock_filter(request, response):
        return request, response

    http_headers = ["Cache-Control"]

    patch_http_requests(mock_context_wrapper, mock_filter, http_headers)

    assert hasattr(RequestsSession, "__monkey_patched")
    assert hasattr(BotocoreSession, "__monkey_patched")
    assert hasattr(BotocoreVendoredSession, "__monkey_patched")

    requests_session = RequestsSession()
    requests_session.send()
    assert mock_requests_session_send.called

    botocore_session = BotocoreSession()
    botocore_session.send()
    assert mock_botocore_session_send.called

    botocore_vendored_session = BotocoreVendoredSession()
    botocore_vendored_session.send()
    assert mock_botocore_vendored_session_send.called

    restore_http_requests()

    assert not hasattr(RequestsSession, "__monkey_patched")
    assert not hasattr(BotocoreSession, "__monkey_patched")
    assert not hasattr(BotocoreVendoredSession, "__monkey_patched")


@mock.patch("iopipe.contrib.trace.auto_http.original_requests_session_send")
@mock.patch("iopipe.contrib.trace.auto_http.original_botocore_session_send")
@mock.patch("iopipe.contrib.trace.auto_http.original_botocore_vendored_session_send")
def test_monkey_patching_no_iopipe(
    mock_botocore_vendored_session_send,
    mock_botocore_session_send,
    mock_requests_session_send,
    mock_context,
):
    assert not hasattr(RequestsSession, "__monkey_patched")
    assert not hasattr(BotocoreSession, "__monkey_patched")
    assert not hasattr(BotocoreVendoredSession, "__monkey_patched")

    delattr(mock_context, "iopipe")

    patch_http_requests(mock_context, None, None)

    assert hasattr(RequestsSession, "__monkey_patched")
    assert hasattr(BotocoreSession, "__monkey_patched")
    assert hasattr(BotocoreVendoredSession, "__monkey_patched")

    requests_session = RequestsSession()
    requests_session.send()
    assert mock_requests_session_send.called

    botocore_session = BotocoreSession()
    botocore_session.send()
    assert mock_botocore_session_send.called

    botocore_vendored_session = BotocoreVendoredSession()
    botocore_vendored_session.send()
    assert mock_botocore_vendored_session_send.called

    restore_http_requests()

    assert not hasattr(RequestsSession, "__monkey_patched")
    assert not hasattr(BotocoreSession, "__monkey_patched")
    assert not hasattr(BotocoreVendoredSession, "__monkey_patched")
