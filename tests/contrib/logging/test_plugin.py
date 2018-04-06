import mock


@mock.patch('iopipe.contrib.logging.plugin.upload_log_data', autospec=True)
@mock.patch('iopipe.contrib.logging.plugin.get_signed_request', autospec=True)
@mock.patch('iopipe.report.send_report', autospec=True)
def test__logging_plugin(mock_send_report, mock_get_signed_request, mock_upload_log_data, handler_with_logging,
                         mock_context):
    iopipe, handler = handler_with_logging
    plugins = iopipe.plugins

    assert len(plugins) == 1
    assert plugins[0].enabled is True

    mock_get_signed_request.return_value = {
        'jwtAccess': 'foobar',
        'signedRequest': 'https://mock_signed_url',
        'url': 'https://mock_url',
    }

    handler({}, mock_context)

    mock_get_signed_request.assert_called_once_with(iopipe.report, '.log')
    mock_upload_log_data.assert_called_once_with('https://mock_signed_url', mock.ANY)

    plugin = next((p for p in iopipe.report.plugins if p['name'] == 'logging'))
    assert plugin['uploads'][0] == 'foobar'

    stream = iopipe.plugins[0].handler.stream

    assert 'testlog - DEBUG - I got nothing.' not in stream.getvalue()
    assert 'testlog - INFO - I might have something.' in stream.getvalue()
    assert 'testlog - WARNING - Got something.' in stream.getvalue()
    assert 'testlog - ERROR - And you have it, too.' in stream.getvalue()
    assert"testlog - CRITICAL - And it's fatal." in stream.getvalue()


@mock.patch('iopipe.contrib.logging.plugin.upload_log_data', autospec=True)
@mock.patch('iopipe.contrib.logging.plugin.get_signed_request', autospec=True)
@mock.patch('iopipe.report.send_report', autospec=True)
def test__logging_plugin__debug(mock_send_report, mock_get_signed_request, mock_upload_log_data,
                                handler_with_logging_debug, mock_context):
    iopipe, handler = handler_with_logging_debug

    handler({}, mock_context)

    stream = iopipe.plugins[0].handler.stream

    assert 'testlog - DEBUG - I should be logged.' in stream.getvalue()
