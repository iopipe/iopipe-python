import mock
import pytest

from iopipe import constants


@mock.patch("iopipe.report.send_report", autospec=True)
def test_coldstarts(mock_send_report, handler, mock_context, monkeypatch):
    """Assert that cold start is true on first invocation and false on next"""
    monkeypatch.setattr(constants, "COLDSTART", True)
    iopipe, handler = handler

    handler(None, mock_context)
    assert iopipe.report.report["coldstart"] is True
    assert "@iopipe/coldstart" in iopipe.report.labels

    handler(None, mock_context)
    assert iopipe.report.report["coldstart"] is False
    assert "@iopipe/coldstart" not in iopipe.report.labels


@mock.patch("iopipe.report.send_report", autospec=True)
def test_client_id_is_configured(mock_send_report, handler, mock_context):
    """Assert that the agent configures the client_id correctly"""
    iopipe, handler = handler
    handler(None, mock_context)

    assert iopipe.report.report["client_id"] == "test-suite"


@mock.patch("iopipe.report.send_report", autospec=True)
def test_function_name_from_context(mock_send_report, handler, mock_context):
    """Assert that the agent extracts the function name from the context"""
    iopipe, handler = handler
    handler(None, mock_context)

    assert iopipe.report.report["aws"]["functionName"] == "handler"


@mock.patch("iopipe.report.send_report", autospec=True)
def test_custom_metrics(mock_send_report, handler_with_events, mock_context):
    """Assert that the agent collects custom metrics"""
    iopipe, handler = handler_with_events
    handler(None, mock_context)

    assert len(iopipe.report.custom_metrics) == 7
    # Decimals are converted to strings
    assert (
        iopipe.report.custom_metrics[6]["s"]
        == "12.300000000000000710542735760100185871124267578125"
    )
    assert "@iopipe/metrics" in iopipe.report.labels


@mock.patch("iopipe.report.send_report", autospec=True)
def test_labels(mock_send_report, handler_with_labels, mock_context):
    """Assert that the agent collects labels"""
    iopipe, handler = handler_with_labels
    handler(None, mock_context)

    assert len(iopipe.report.labels) == 5


@mock.patch("iopipe.report.send_report", autospec=True)
def test_erroring(mock_send_report, handler_that_errors, mock_context):
    """Assert that the agent catches and traces uncaught exceptions"""
    iopipe, handler = handler_that_errors

    with pytest.raises(ValueError):
        handler(None, mock_context)

    assert iopipe.report.report["errors"]["name"] == "ValueError"
    assert iopipe.report.report["errors"]["message"] == "Behold, a value error"
    assert isinstance(iopipe.report.report["errors"]["stack"], str)
    assert "@iopipe/error" in iopipe.report.labels


@mock.patch("iopipe.report.send_report", autospec=True)
def test_timeouts(mock_send_report, handler_that_timeouts, mock_context):
    """Assert that the agent timeouts before function does"""
    iopipe, handler = handler_that_timeouts
    mock_context.set_remaining_time_in_millis(500)

    try:
        handler(None, mock_context)
    except Exception:
        pass

    assert iopipe.report.report["errors"]["message"] == "Timeout Exceeded."
    assert iopipe.report.report["errors"]["name"] == "TimeoutError"
    assert isinstance(iopipe.report.report["errors"]["stack"], str)
    assert "@iopipe/timeout" in iopipe.report.labels


@mock.patch("iopipe.report.send_report", autospec=True)
def test_timeouts_disable(mock_send_report, handler_that_timeouts, mock_context):
    """Assert the timeout is disabled if insufficient time remaining"""
    iopipe, handler = handler_that_timeouts

    # The default is 0.15, so 150 / 1000 - 0.15 = 0
    mock_context.set_remaining_time_in_millis(150)

    with pytest.raises(Exception):
        handler(None, mock_context)

    # Exception will occur because timeout is disabled
    assert iopipe.report.report["errors"] != {}
    assert iopipe.report.report["errors"]["name"] == "Exception"
    assert (
        iopipe.report.report["errors"]["message"]
        == "Should timeout before this is raised"
    )


@mock.patch("iopipe.report.send_report", autospec=True)
def test_sync_http(mock_send_report, handler_with_sync_http, mock_context):
    """Assert that the agent still works synchronously"""
    iopipe, handler = handler_with_sync_http

    handler({}, mock_context)

    assert iopipe.report.sent


def test_validate_context(iopipe, mock_context):
    """Asserts that contexts are validated correctly"""
    assert iopipe.validate_context(mock_context) is True

    class InvalidContext(object):
        pass

    invalid_context = InvalidContext()

    assert iopipe.validate_context(invalid_context) is False


def test_disabled_reporting(handler_that_disables_reporting, mock_context):
    """Assert that reporting is disabled for an invocation"""
    iopipe, handler = handler_that_disables_reporting
    handler(None, mock_context)

    assert iopipe.report.sent is False


def test_disabled_reporting_with_error(
    handler_that_disables_reporting_with_error, mock_context
):
    """Assert that reporting is disabled for an invocation with error"""
    iopipe, handler = handler_that_disables_reporting_with_error

    with pytest.raises(Exception):
        handler(None, mock_context)

    assert iopipe.report.sent is False


@mock.patch("iopipe.report.send_report", autospec=True)
def test_context_attribute(mock_send_report, handler, mock_context):
    """Assert that the current context is available as an iopipe attribute"""
    iopipe, handler = handler

    assert hasattr(iopipe, "context")
    assert iopipe.context is None

    handler(None, mock_context)

    assert iopipe.context is not None


@mock.patch("iopipe.report.send_report", autospec=True)
def test_double_instrumentation(mock_send_report, handler, mock_context, monkeypatch):
    """Assert that a function can only be instrumented once"""
    iopipe, handler = handler

    double_wrapped = iopipe(handler)

    double_wrapped(None, mock_context)

    assert mock_send_report.call_count == 1
