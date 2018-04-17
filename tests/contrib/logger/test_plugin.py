from datetime import datetime
import json
import mock


@mock.patch('iopipe.contrib.logger.plugin.upload_log_data', autospec=True)
@mock.patch('iopipe.contrib.logger.plugin.get_signed_request', autospec=True)
@mock.patch('iopipe.report.send_report', autospec=True)
def test__logger_plugin(mock_send_report, mock_get_signed_request, mock_upload_log_data, handler_with_logger,
                        mock_context):
    iopipe, handler = handler_with_logger
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

    plugin = next((p for p in iopipe.report.plugins if p['name'] == 'logger'))
    assert plugin['uploads'][0] == 'foobar'

    stream = iopipe.plugins[0].handler.stream

    assert '"message": "I got nothing.", "name": "testlog", "severity": "DEBUG"' not in stream.getvalue()
    assert '"message": "I might have something.", "name": "testlog", "severity": "INFO"' in stream.getvalue()
    assert '"message": "Got something.", "name": "testlog", "severity": "WARNING"' in stream.getvalue()
    assert '"message": "And you have it, too.", "name": "testlog", "severity": "ERROR"' in stream.getvalue()
    assert '"message": "And it\'s fatal.", "name": "testlog", "severity": "CRITICAL"' in stream.getvalue()

    assert '"message": "This is not a misprint.", "name": "testlog", "severity": "INFO"' in stream.getvalue()

    stream.seek(0)

    for line in stream.readlines():
        json_msg = json.loads(line)
        assert 'timestamp' in json_msg
        assert isinstance(datetime.strptime(json_msg['timestamp'], '%Y-%m-%d %H:%M:%S.%f'), datetime)


@mock.patch('iopipe.contrib.logger.plugin.upload_log_data', autospec=True)
@mock.patch('iopipe.contrib.logger.plugin.get_signed_request', autospec=True)
@mock.patch('iopipe.report.send_report', autospec=True)
def test__logger_plugin__debug(mock_send_report, mock_get_signed_request, mock_upload_log_data,
                               handler_with_logger_debug, mock_context):
    iopipe, handler = handler_with_logger_debug

    handler({}, mock_context)

    stream = iopipe.plugins[0].handler.stream

    assert '"message": "I should be logged.", "name": "testlog", "severity": "DEBUG"' in stream.getvalue()


@mock.patch('iopipe.contrib.logger.plugin.upload_log_data', autospec=True)
@mock.patch('iopipe.contrib.logger.plugin.get_signed_request', autospec=True)
@mock.patch('iopipe.report.send_report', autospec=True)
def test__logger_plugin__use_tmp(mock_send_report, mock_get_signed_request, mock_upload_log_data,
                                 handler_with_logger_use_tmp, mock_context):
    iopipe, handler = handler_with_logger_use_tmp

    handler({}, mock_context)

    stream = iopipe.plugins[0].handler.stream

    assert hasattr(stream, 'file')
    assert stream.file.closed
