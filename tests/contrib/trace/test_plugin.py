import mock


@mock.patch("iopipe.report.send_report", autospec=True)
def test__trace_plugin(mock_send_report, handler_with_trace, mock_context):
    iopipe, handler = handler_with_trace

    assert len(iopipe.config["plugins"]) == 1

    handler({}, mock_context)

    assert len(iopipe.report.performance_entries) == 3
    assert any([e["name"] == "measure:foo" for e in iopipe.report.performance_entries])
    assert "@iopipe/plugin-trace" in iopipe.report.labels
    assert "@iopipe/metrics" not in iopipe.report.labels


@mock.patch("iopipe.report.send_report", autospec=True)
def test__trace_plugin_no_auto_measure(
    mock_send_report, handler_with_trace_no_auto_measure, mock_context
):
    iopipe, handler = handler_with_trace_no_auto_measure

    assert len(iopipe.config["plugins"]) == 1

    handler({}, mock_context)

    assert len(iopipe.report.performance_entries) == 2
    assert not any(
        [e["name"] == "measure:foo" for e in iopipe.report.performance_entries]
    )


@mock.patch("iopipe.report.send_report", autospec=True)
def test__trace_plugin__valid_schema(
    mock_send_report, handler_with_trace, mock_context, assert_valid_schema
):
    iopipe, handler = handler_with_trace

    handler({}, mock_context)

    assert_valid_schema(
        iopipe.report.report,
        optional_fields=[
            "environment.nodejs",
            "environment.runtime.vendor",
            "environment.runtime.vmVendor",
            "environment.runtime.vmVersion",
            "errors.count",
            "errors.message",
            "errors.name",
            "errors.stack",
            "errors.stackHash",
            "httpTraceEntries",
            "labels",
            "memory",
            "plugins.uploads",
            "projectId",
        ],
    )


@mock.patch("iopipe.report.send_report", autospec=True)
def test__trace_plugin__auto_http__http(
    mock_send_report, handler_with_trace_auto_http, mock_context
):
    iopipe, handler = handler_with_trace_auto_http

    assert len(iopipe.config["plugins"]) == 1

    handler({}, mock_context)

    traces = iopipe.report.http_trace_entries

    assert len(traces) == 2


@mock.patch("iopipe.report.send_report", autospec=True)
def test_trace_plugin__auto_http__https(
    mock_send_report, handler_with_trace_auto_https, mock_context
):
    iopipe, handler = handler_with_trace_auto_https

    assert len(iopipe.config["plugins"]) == 1

    handler({}, mock_context)

    traces = iopipe.report.http_trace_entries

    assert len(traces) == 1


@mock.patch("iopipe.report.send_report", autospec=True)
def test_trace_plugin__auto_http__filter(
    mock_send_report, handler_with_trace_auto_http_filter, mock_context
):
    iopipe, handler = handler_with_trace_auto_http_filter

    handler({}, mock_context)

    assert len(iopipe.report.http_trace_entries) == 0
