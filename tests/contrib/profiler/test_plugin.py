import mock


@mock.patch('iopipe.report.send_report', autospec=True)
def test__profiler_plugin(mock_send_report, handler_with_profiler, mock_context):
    iopipe, handler = handler_with_profiler

    assert len(iopipe.config['plugins']) == 1

    #handler({}, mock_context)
