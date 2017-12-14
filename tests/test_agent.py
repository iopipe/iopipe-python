import mock

from iopipe import constants


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
    mock_context.set_remaining_time_in_millis(2000)

    try:
        handler(None, mock_context)
    except Exception:
         pass

    assert iopipe.report.report['errors'] == {}
    mock_send_report.assert_called_once_with(iopipe.report.report, iopipe.config)


@mock.patch('iopipe.report.send_report', autospec=True)
def test_timeouts_disable(mock_send_report, handler_that_timeouts, mock_context):
    """Assert the timeout is disabled if insufficient time remaining"""
    iopipe, handler = handler_that_timeouts

    # The default is 1.5, so 1500 / 100 - 1.5 = 0
    mock_context.set_remaining_time_in_millis(1500)

    try:
        handler(None, mock_context)
    except Exception:
         pass

    # Exception will occur because timeout is disabled
    assert iopipe.report.report['errors'] != {}
    assert iopipe.report.report['errors']['name'] == 'Exception'
    assert iopipe.report.report['errors']['message'] == 'Should timeout before this is raised'
