import mock


@mock.patch('iopipe.report.send_report', autospec=True)
def test__eventinfo_plugin__apigw(mock_send_report, handler_with_eventinfo, event_apigw, mock_context):
    iopipe, handler = handler_with_eventinfo
    plugins = iopipe.config['plugins']

    assert len(plugins) == 1
    assert plugins[0].enabled is True
    assert plugins[0].name == 'event-info'

    handler(event_apigw, mock_context)
    metrics = iopipe.report.custom_metrics

    assert any([m['name'] == '@iopipe/event-info.eventType' for m in metrics])
    assert len(metrics) == 10

    event_type = [m for m in metrics if m['name'] == '@iopipe/event-info.eventType']
    assert len(event_type) == 1
    assert event_type[0]['s'] == 'apiGateway'


@mock.patch('iopipe.report.send_report', autospec=True)
def test__eventinfo_plugin__cloudfront(mock_send_report, handler_with_eventinfo, event_cloudfront, mock_context):
    iopipe, handler = handler_with_eventinfo
    plugins = iopipe.config['plugins']

    assert len(plugins) == 1
    assert plugins[0].enabled is True
    assert plugins[0].name == 'event-info'

    handler(event_cloudfront, mock_context)
    metrics = iopipe.report.custom_metrics

    assert any([m['name'] == '@iopipe/event-info.eventType' for m in metrics])
    assert len(metrics) == 7

    event_type = [m for m in metrics if m['name'] == '@iopipe/event-info.eventType']
    assert len(event_type) == 1
    assert event_type[0]['s'] == 'cloudFront'


@mock.patch('iopipe.report.send_report', autospec=True)
def test__eventinfo_plugin__kinesis(mock_send_report, handler_with_eventinfo, event_kinesis, mock_context):
    iopipe, handler = handler_with_eventinfo
    plugins = iopipe.config['plugins']

    assert len(plugins) == 1
    assert plugins[0].enabled is True
    assert plugins[0].name == 'event-info'

    handler(event_kinesis, mock_context)
    metrics = iopipe.report.custom_metrics

    assert any([m['name'] == '@iopipe/event-info.eventType' for m in metrics])
    assert len(metrics) == 4

    event_type = [m for m in metrics if m['name'] == '@iopipe/event-info.eventType']
    assert len(event_type) == 1
    assert event_type[0]['s'] == 'kinesis'


@mock.patch('iopipe.report.send_report', autospec=True)
def test__eventinfo_plugin__scheduled(mock_send_report, handler_with_eventinfo, event_scheduled, mock_context):
    iopipe, handler = handler_with_eventinfo
    plugins = iopipe.config['plugins']

    assert len(plugins) == 1
    assert plugins[0].enabled is True
    assert plugins[0].name == 'event-info'

    handler(event_scheduled, mock_context)
    metrics = iopipe.report.custom_metrics

    assert any([m['name'] == '@iopipe/event-info.eventType' for m in metrics])
    assert len(metrics) == 6

    event_type = [m for m in metrics if m['name'] == '@iopipe/event-info.eventType']
    assert len(event_type) == 1
    assert event_type[0]['s'] == 'scheduled'
