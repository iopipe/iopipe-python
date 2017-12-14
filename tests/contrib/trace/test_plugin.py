import mock


@mock.patch('iopipe.report.send_report', autospec=True)
def test_plugin(mock_send_report, handler_with_plugin, mock_context):
    iopipe, handler = handler_with_plugin

    assert len(iopipe.plugins) == 1

    handler({}, mock_context)

    assert len(iopipe.report.report['performanceEntries']) == 4


@mock.patch('iopipe.report.send_report', autospec=True)
def test_plugin_auto_measure(mock_send_report, handler_with_auto_measure, mock_context):
    iopipe, handler = handler_with_auto_measure

    assert len(iopipe.plugins) == 1

    handler({}, mock_context)

    assert len(iopipe.report.report['performanceEntries']) == 6
