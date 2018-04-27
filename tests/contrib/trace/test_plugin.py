import mock


@mock.patch("iopipe.report.send_report", autospec=True)
def test__trace_plugin(mock_send_report, handler_with_trace, mock_context):
    iopipe, handler = handler_with_trace

    assert len(iopipe.config["plugins"]) == 1

    handler({}, mock_context)

    assert len(iopipe.report.report["performanceEntries"]) == 3
    assert any(
        [e["name"] == "measure:foo" for e in iopipe.report.report["performanceEntries"]]
    )
    assert "@iopipe/plugin-trace" in iopipe.report.labels
    assert "@iopipe/metrics" not in iopipe.report.labels


@mock.patch("iopipe.report.send_report", autospec=True)
def test__trace_plugin_no_auto_measure(
    mock_send_report, handler_with_trace_no_auto_measure, mock_context
):
    iopipe, handler = handler_with_trace_no_auto_measure

    assert len(iopipe.config["plugins"]) == 1

    handler({}, mock_context)

    assert len(iopipe.report.report["performanceEntries"]) == 2
    assert not any(
        [e["name"] == "measure:foo" for e in iopipe.report.report["performanceEntries"]]
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

    metrics = iopipe.report.report["custom_metrics"]
    traces = iopipe.report.report["performanceEntries"]

    assert len(traces) == 6
    assert len(metrics) == 50
    assert all([m["name"].startswith("@iopipe/trace.") for m in metrics])
    assert any(
        [
            m["s"] == "autoHttp"
            for m in metrics
            if m["name"].startswith("@iopipe/trace.") and m["name"].endswith(".type")
        ]
    )


@mock.patch("iopipe.report.send_report", autospec=True)
def test_trace_plugin__auto_http__https(
    mock_send_report, handler_with_trace_auto_https, mock_context
):
    iopipe, handler = handler_with_trace_auto_https

    assert len(iopipe.config["plugins"]) == 1

    handler({}, mock_context)

    metrics = iopipe.report.report["custom_metrics"]
    traces = iopipe.report.report["performanceEntries"]

    assert len(traces) == 3
    assert len(metrics) == 25
    assert all([m["name"].startswith("@iopipe/trace.") for m in metrics])
    assert any(
        [
            m["s"] == "autoHttp"
            for m in metrics
            if m["name"].startswith("@iopipe/trace.") and m["name"].endswith(".type")
        ]
    )

    id = next(
        (m["name"].split(".", 2)[1] for m in metrics if m["name"].endswith(".type"))
    )
    metric_map = {m["name"]: m.get("s", m.get("n")) for m in metrics}
    expected_key_value = {
        "@iopipe/trace.%s.request.hash" % id: "",
        "@iopipe/trace.%s.request.headers.Accept" % id: "*/*",
        "@iopipe/trace.%s.request.headers.Accept-Encoding" % id: "gzip, deflate",
        "@iopipe/trace.%s.request.headers.Connection" % id: "keep-alive",
        "@iopipe/trace.%s.request.headers.User-Agent" % id: None,
        "@iopipe/trace.%s.request.hostname" % id: "www.iopipe.com",
        "@iopipe/trace.%s.request.method" % id: "GET",
        "@iopipe/trace.%s.request.path" % id: "/",
        "@iopipe/trace.%s.request.port" % id: None,
        "@iopipe/trace.%s.request.protocol" % id: "https",
        "@iopipe/trace.%s.request.query" % id: "",
        "@iopipe/trace.%s.request.url" % id: "https://www.iopipe.com/",
        "@iopipe/trace.%s.response.headers.Age" % id: None,
        "@iopipe/trace.%s.response.headers.Cache-Control"
        % id: "public, max-age=0, must-revalidate",
        "@iopipe/trace.%s.response.headers.Connection" % id: "keep-alive",
        "@iopipe/trace.%s.response.headers.Content-Encoding" % id: "gzip",
        "@iopipe/trace.%s.response.headers.Content-Length" % id: None,
        "@iopipe/trace.%s.response.headers.Content-Type"
        % id: "text/html; charset=UTF-8",
        "@iopipe/trace.%s.response.headers.Date" % id: None,
        "@iopipe/trace.%s.response.headers.Etag" % id: None,
        "@iopipe/trace.%s.response.headers.Server" % id: None,
        "@iopipe/trace.%s.response.headers.Strict-Transport-Security" % id: None,
        "@iopipe/trace.%s.response.headers.Vary" % id: "Accept-Encoding",
        "@iopipe/trace.%s.response.statusCode" % id: 200,
        "@iopipe/trace.%s.type" % id: "autoHttp",
    }

    for key, value in metric_map.items():
        assert key in expected_key_value
        if expected_key_value[key] is not None:
            assert expected_key_value[key] == value


@mock.patch("iopipe.report.send_report", autospec=True)
def test_trace_plugin__auto_http__filter(
    mock_send_report, handler_with_trace_auto_http_filter, mock_context
):
    iopipe, handler = handler_with_trace_auto_http_filter

    handler({}, mock_context)

    assert len(iopipe.report.report["custom_metrics"]) == 0
    assert len(iopipe.report.report["performanceEntries"]) == 0
