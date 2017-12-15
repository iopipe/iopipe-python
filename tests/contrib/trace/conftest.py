import pytest

from iopipe import IOpipe
from iopipe.contrib.trace import TracePlugin
from iopipe.contrib.trace.timeline import Timeline
from tests.mock_context import MockContext


@pytest.fixture
def iopipe_with_plugin():
    plugin = TracePlugin()
    return IOpipe(
        token='test-suite',
        url='https://metrics-api.iopipe.com',
        debug=True,
        plugins=[plugin])


@pytest.fixture
def iopipe_with_auto_measure():
    plugin = TracePlugin(auto_measure=True)
    return IOpipe(
        token='test-suite',
        url='https://metrics-api.iopipe.com',
        debug=True,
        plugins=[plugin])


@pytest.fixture
def mock_context():
    return MockContext('handler', '$LATEST')


@pytest.fixture
def handler_with_plugin(iopipe_with_plugin):
    @iopipe_with_plugin
    def _handler(event, context):
        assert hasattr(context, 'iopipe')
        assert hasattr(context.iopipe, 'mark')
        assert hasattr(context.iopipe.mark, 'start')
        assert hasattr(context.iopipe.mark, 'end')
        assert hasattr(context.iopipe.mark, 'measure')

        context.iopipe.mark.start('foo')
        context.iopipe.mark.end('foo')
    return iopipe_with_plugin, _handler


@pytest.fixture
def handler_with_auto_measure(iopipe_with_auto_measure):
    @iopipe_with_auto_measure
    def _handler(event, context):
        assert hasattr(context, 'iopipe')
        assert hasattr(context.iopipe, 'mark')
        assert hasattr(context.iopipe.mark, 'start')
        assert hasattr(context.iopipe.mark, 'end')
        assert hasattr(context.iopipe.mark, 'measure')

        context.iopipe.mark.start('foo')
        context.iopipe.mark.end('foo')
    return iopipe_with_auto_measure, _handler


@pytest.fixture
def timeline():
    return Timeline()
