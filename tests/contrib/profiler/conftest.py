import pytest

from iopipe import IOpipe
from iopipe.contrib.profiler import ProfilerPlugin


@pytest.fixture
def iopipe_with_profiler():
    plugin = ProfilerPlugin(enabled=True)
    return IOpipe(token='test-suite', url='https://metrics-api.iopipe.com', debug=True, plugins=[plugin])


@pytest.fixture
def handler_with_profiler(iopipe_with_profiler):
    @iopipe_with_profiler
    def _handler(event, context):
        assert hasattr(context, 'iopipe')
        assert hasattr(context.iopipe, 'mark')
        assert hasattr(context.iopipe.mark, 'start')
        assert hasattr(context.iopipe.mark, 'end')
        assert hasattr(context.iopipe.mark, 'measure')

        context.iopipe.mark.start('foo')
        context.iopipe.mark.end('foo')

    return iopipe_with_profiler, _handler
