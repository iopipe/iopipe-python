import pytest
import requests

from iopipe import IOpipeCore
from iopipe.contrib.trace.marker import Marker
from iopipe.contrib.trace import TracePlugin
from iopipe.contrib.trace.timeline import Timeline


@pytest.fixture
def iopipe_with_trace():
    plugin = TracePlugin()
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def iopipe_with_trace_no_auto_measure():
    plugin = TracePlugin(auto_measure=False)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def iopipe_with_trace_auto_http():
    plugin = TracePlugin(auto_http=True)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def iopipe_with_trace_auto_http_filter():
    def http_filter(request, response):
        if request["url"].startswith("https://www.iopipe.com"):
            raise Exception("Do not trace this URL")

    plugin = TracePlugin(auto_http=True, http_filter=http_filter)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def handler_with_trace(iopipe_with_trace):
    @iopipe_with_trace
    def _handler(event, context):
        assert hasattr(context, "iopipe")
        assert hasattr(context.iopipe, "mark")
        assert hasattr(context.iopipe.mark, "start")
        assert hasattr(context.iopipe.mark, "end")
        assert hasattr(context.iopipe.mark, "measure")

        context.iopipe.mark.start("foo")
        context.iopipe.mark.end("foo")

    return iopipe_with_trace, _handler


@pytest.fixture
def handler_with_trace_no_auto_measure(iopipe_with_trace_no_auto_measure):
    @iopipe_with_trace_no_auto_measure
    def _handler(event, context):
        assert hasattr(context, "iopipe")
        assert hasattr(context.iopipe, "mark")
        assert hasattr(context.iopipe.mark, "start")
        assert hasattr(context.iopipe.mark, "end")
        assert hasattr(context.iopipe.mark, "measure")

        context.iopipe.mark.start("foo")
        context.iopipe.mark.end("foo")

    return iopipe_with_trace_no_auto_measure, _handler


@pytest.fixture
def handler_with_trace_auto_http(iopipe_with_trace_auto_http):
    @iopipe_with_trace_auto_http
    def _handler(event, context):
        requests.get("http://www.iopipe.com/")

    return iopipe_with_trace_auto_http, _handler


@pytest.fixture
def handler_with_trace_auto_https(iopipe_with_trace_auto_http):
    @iopipe_with_trace_auto_http
    def _handler(event, context):
        requests.get("https://www.iopipe.com/")

    return iopipe_with_trace_auto_http, _handler


@pytest.fixture
def handler_with_trace_auto_http_filter(iopipe_with_trace_auto_http_filter):
    @iopipe_with_trace_auto_http_filter
    def _handler(event, context):
        requests.get("https://www.iopipe.com/")

    return iopipe_with_trace_auto_http_filter, _handler


@pytest.fixture
def iopipe_with_trace_auto_http_filter_request():
    def http_filter(request, response):
        return None, response

    plugin = TracePlugin(auto_http=True, http_filter=http_filter)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def handler_with_trace_auto_http_filter_request(
    iopipe_with_trace_auto_http_filter_request
):
    @iopipe_with_trace_auto_http_filter_request
    def _handler(event, context):
        requests.get("https://www.iopipe.com/")

    return iopipe_with_trace_auto_http_filter_request, _handler


@pytest.fixture
def marker(timeline, mock_context):
    return Marker(timeline, mock_context)


@pytest.fixture
def timeline():
    return Timeline()
