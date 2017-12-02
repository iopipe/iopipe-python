import time

import mock
import pytest

from iopipe import constants, IOpipe

from .mock_context import MockContext


@pytest.fixture
def iopipe():
    return IOpipe('test-suite', 'https://metrics-api.iopipe.com', True)


@pytest.fixture
def mock_context():
    return MockContext('handler', '$LATEST')


@pytest.fixture
def handler(iopipe):
    @iopipe.decorator
    def _handler(event, context):
        pass
    return iopipe, _handler


@pytest.fixture
def handler_with_events(iopipe):
    @iopipe.decorator
    def _handler_with_events(event, context):
        iopipe.log('somekey', 2)
        iopipe.log('anotherkey', 'qualitative value')
    return iopipe, _handler_with_events


@pytest.fixture
def handler_that_errors(iopipe):
    @iopipe.decorator
    def _handler_that_errors(event, context):
        raise ValueError("Behold, a value error")
    return iopipe, _handler_that_errors


@pytest.fixture
def handler_that_timeouts(iopipe):
    @iopipe.decorator
    def _handler_that_timeouts(event, context):
        time.sleep(5)
        raise Exception('Should timeout before this is raised')
    return iopipe, _handler_that_timeouts


@mock.patch('iopipe.report.send_report', autospec=True)
def test_coldstarts(mock_send_report, handler, mock_context, monkeypatch):
    """Assert that cold start is true on first invocation and false on next"""
    monkeypatch.setattr(constants, 'COLDSTART', True)
    iopipe, handler = handler

    handler(None, mock_context)
    assert iopipe.report.report['coldstart'] is True

    handler(None, mock_context)
    assert iopipe.report.report['coldstart'] is False


@mock.patch('iopipe.report.send_report', autospec=True)
def test_client_id_is_configured(mock_send_report, handler, mock_context):
    """Assert that the agent configures the client_id correctly"""
    iopipe, handler = handler
    handler(None, mock_context)

    assert iopipe.report.report['client_id'] == 'test-suite'
    mock_send_report.assert_called_once_with(iopipe.report.report, iopipe.config)


@mock.patch('iopipe.report.send_report', autospec=True)
def test_function_name_from_context(mock_send_report, handler, mock_context):
    """Assert that the agent extracts the function name from the context"""
    iopipe, handler = handler
    handler(None, mock_context)

    assert iopipe.report.report['aws']['functionName'] == 'handler'
    mock_send_report.assert_called_once_with(iopipe.report.report, iopipe.config)


@mock.patch('iopipe.report.send_report', autospec=True)
def test_custom_metrics(mock_send_report, handler_with_events, mock_context):
    """Assert that the agent collects custom metrics"""
    iopipe, handler = handler_with_events
    handler(None, mock_context)

    assert len(iopipe.report.custom_metrics) == 2
    mock_send_report.assert_called_once_with(iopipe.report.report, iopipe.config)


@mock.patch('iopipe.report.send_report', autospec=True)
def test_erroring(mock_send_report, handler_that_errors, mock_context):
    """Assert that the agent catches and traces uncaught exceptions"""
    iopipe, handler = handler_that_errors

    try:
        handler(None, mock_context)
    except Exception:
        pass

    assert iopipe.report.report['errors']['name'] == 'ValueError'
    assert iopipe.report.report['errors']['message'] == 'Behold, a value error'
    mock_send_report.assert_called_once_with(iopipe.report.report, iopipe.config)


@mock.patch('iopipe.report.send_report', autospec=True)
def test_timeouts(mock_send_report, handler_that_timeouts, mock_context):
    """Assert that the agent timeouts before function does"""
    iopipe, handler = handler_that_timeouts
    mock_context.set_remaining_time_in_millis(200)

    try:
        handler(None, mock_context)
    except Exception:
         pass

    assert iopipe.report.report['errors'] == {}
    mock_send_report.assert_called_once_with(iopipe.report.report, iopipe.config)
