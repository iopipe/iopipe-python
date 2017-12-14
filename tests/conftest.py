import time

import pytest

from iopipe import IOpipe

from .mock_context import MockContext


@pytest.fixture
def iopipe():
    return IOpipe('test-suite', 'https://metrics-api.iopipe.com', True)


@pytest.fixture
def mock_context():
    return MockContext('handler', '$LATEST')


@pytest.fixture
def handler(iopipe):
    @iopipe.decorator
    def _handler(event, context):
        pass
    return iopipe, _handler


@pytest.fixture
def handler_with_events(iopipe):
    @iopipe.decorator
    def _handler_with_events(event, context):
        iopipe.log('somekey', 2)
        iopipe.log('anotherkey', 'qualitative value')
    return iopipe, _handler_with_events


@pytest.fixture
def handler_that_errors(iopipe):
    @iopipe.decorator
    def _handler_that_errors(event, context):
        raise ValueError("Behold, a value error")
    return iopipe, _handler_that_errors


@pytest.fixture
def handler_that_timeouts(iopipe):
    @iopipe.decorator
    def _handler_that_timeouts(event, context):
        time.sleep(2)
        raise Exception('Should timeout before this is raised')
    return iopipe, _handler_that_timeouts
