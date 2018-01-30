import mock


@mock.patch('iopipe.report.send_report', autospec=True)
def test__trace_plugin(mock_send_report, handler_with_plugin, mock_context):
    iopipe, handler = handler_with_plugin

    assert len(iopipe.config['plugins']) == 1

    handler({}, mock_context)

    assert len(iopipe.report.report['performanceEntries']) == 4
    assert not any([e['name'] == 'measure:foo' for e in iopipe.report.report['performanceEntries']])
    assert not any([e['name'] == 'measure:iopipe' for e in iopipe.report.report['performanceEntries']])


@mock.patch('iopipe.report.send_report', autospec=True)
def test__trace_plugin_auto_measure(mock_send_report, handler_with_auto_measure, mock_context):
    iopipe, handler = handler_with_auto_measure

    assert len(iopipe.config['plugins']) == 1

    handler({}, mock_context)

    assert len(iopipe.report.report['performanceEntries']) == 6
    assert any([e['name'] == 'measure:foo' for e in iopipe.report.report['performanceEntries']])
    assert any([e['name'] == 'measure:iopipe' for e in iopipe.report.report['performanceEntries']])


@mock.patch('iopipe.report.send_report', autospec=True)
def test__trace_plugin__valid_schema(mock_send_report, handler_with_auto_measure, mock_context, assert_valid_schema):
    iopipe, handler = handler_with_auto_measure

    handler({}, mock_context)

    assert_valid_schema(iopipe.report.report, optional_fields=[
        'aws.traceId',
        'environment.runtime.vendor',
        'environment.runtime.vmVendor',
        'environment.runtime.vmVersion',
        'environment.nodejs',
        'errors.count',
        'errors.message',
        'errors.name',
        'errors.stack',
        'errors.stackHash',
        'memory',
        'projectId',
    ])
