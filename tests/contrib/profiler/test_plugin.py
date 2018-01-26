import mock


@mock.patch('iopipe.contrib.profiler.plugin.upload_profiler_report', autospec=True)
@mock.patch('iopipe.contrib.profiler.plugin.get_signed_request', autospec=True)
@mock.patch('iopipe.report.send_report', autospec=True)
def test__profiler_plugin(mock_send_report, mock_get_signed_request, mock_upload_profiler_report, handler_with_profiler,
                          mock_context):
    iopipe, handler = handler_with_profiler
    plugins = iopipe.config['plugins']

    assert len(plugins) == 1
    assert plugins[0].enabled is True

    mock_get_signed_request.return_value = {'signedRequest': 'https://mock_signed_url'}

    handler({}, mock_context)

    mock_get_signed_request.assert_called_once_with(iopipe.report)
    mock_upload_profiler_report.assert_called_once_with('https://mock_signed_url', plugins[0].stream)

    stream = plugins[0].stream
    stream.seek(0)
    profile = stream.readlines()

    assert 'function calls in' in profile[0]
    assert 'Ordered by: cumulative time' in profile[2]
