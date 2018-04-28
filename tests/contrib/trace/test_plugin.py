import mock


@mock.patch('iopipe.report.send_report', autospec=True)
def test__trace_plugin(mock_send_report, handler_with_trace, mock_context):
    iopipe, handler = handler_with_trace

    assert len(iopipe.config['plugins']) == 1

    handler({}, mock_context)

    assert len(iopipe.report.report['performanceEntries']) == 3
    assert any([e['name'] == 'measure:foo' for e in iopipe.report.report['performanceEntries']])
    assert '@iopipe/trace' in iopipe.report.labels


@mock.patch('iopipe.report.send_report', autospec=True)
def test__trace_plugin_no_auto_measure(mock_send_report, handler_with_trace_no_auto_measure, mock_context):
    iopipe, handler = handler_with_trace_no_auto_measure

    assert len(iopipe.config['plugins']) == 1

    handler({}, mock_context)

    assert len(iopipe.report.report['performanceEntries']) == 2
    assert not any([e['name'] == 'measure:foo' for e in iopipe.report.report['performanceEntries']])


@mock.patch('iopipe.report.send_report', autospec=True)
def test__trace_plugin__valid_schema(mock_send_report, handler_with_trace, mock_context, assert_valid_schema):
    iopipe, handler = handler_with_trace

    handler({}, mock_context)

    assert_valid_schema(
        iopipe.report.report,
        optional_fields=[
            'environment.runtime.vendor',
            'environment.runtime.vmVendor',
            'environment.runtime.vmVersion',
            'environment.nodejs',
            'errors.count',
            'errors.message',
            'errors.name',
            'errors.stack',
            'errors.stackHash',
            'labels',
            'memory',
            'projectId',
            'plugins.uploads',
        ])
