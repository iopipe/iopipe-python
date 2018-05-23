import pytest
import time

from iopipe import IOpipeCore
from iopipe.contrib.profiler import ProfilerPlugin


@pytest.fixture
def iopipe_with_profiler():
    plugin = ProfilerPlugin(enabled=True)
    return IOpipeCore(token='test-suite', url='https://metrics-api.iopipe.com', debug=True, plugins=[plugin])


@pytest.fixture
def handler_with_profiler(iopipe_with_profiler):
    @iopipe_with_profiler
    def _handler(event, context):
        time.sleep(0.1)

    return iopipe_with_profiler, _handler
