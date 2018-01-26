import pytest

from iopipe import IOpipe
from iopipe.contrib.trace.marker import Marker
from iopipe.contrib.trace import TracePlugin
from iopipe.contrib.trace.timeline import Timeline


@pytest.fixture
def iopipe_with_trace():
    plugin = TracePlugin()
    return IOpipe(token='test-suite', url='https://metrics-api.iopipe.com', debug=True, plugins=[plugin])


@pytest.fixture
def iopipe_with_trace_auto_measure():
    plugin = TracePlugin(auto_measure=True)
    return IOpipe(token='test-suite', url='https://metrics-api.iopipe.com', debug=True, plugins=[plugin])


@pytest.fixture
def handler_with_trace(iopipe_with_trace):
    @iopipe_with_trace
    def _handler(event, context):
        assert hasattr(context, 'iopipe')
        assert hasattr(context.iopipe, 'mark')
        assert hasattr(context.iopipe.mark, 'start')
        assert hasattr(context.iopipe.mark, 'end')
        assert hasattr(context.iopipe.mark, 'measure')

        context.iopipe.mark.start('foo')
        context.iopipe.mark.end('foo')

    return iopipe_with_trace, _handler


@pytest.fixture
def handler_with_trace_auto_measure(iopipe_with_trace_auto_measure):
    @iopipe_with_trace_auto_measure
    def _handler(event, context):
        assert hasattr(context, 'iopipe')
        assert hasattr(context.iopipe, 'mark')
        assert hasattr(context.iopipe.mark, 'start')
        assert hasattr(context.iopipe.mark, 'end')
        assert hasattr(context.iopipe.mark, 'measure')

        context.iopipe.mark.start('foo')
        context.iopipe.mark.end('foo')

    return iopipe_with_trace_auto_measure, _handler


@pytest.fixture
def marker(timeline):
    return Marker(timeline)


@pytest.fixture
def timeline():
    return Timeline()
