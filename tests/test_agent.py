import time

import pytest

from iopipe.iopipe import IOpipe

from .MockContext import MockContext


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


# N.B. this must be the first test!
def test_coldstarts(handler, mock_context):
    iopipe, handler = handler
    handler(None, mock_context)
    assert iopipe.report.coldstart

    handler(None, mock_context)
    assert not iopipe.report.coldstart


def test_client_id_is_configured(handler, mock_context):
    iopipe, handler = handler
    handler(None, mock_context)
    assert iopipe.report.client_id == 'test-suite'


def test_function_name_from_context(handler, mock_context):
    iopipe, handler = handler
    handler(None, mock_context)
    assert iopipe.report.aws['functionName'] == 'handler'


def test_custom_metrics(handler_with_events, mock_context):
    iopipe, handler = handler_with_events
    handler(None, mock_context)
    assert len(iopipe.report.custom_metrics) == 2


def test_erroring(handler_that_errors, mock_context):
    iopipe, handler = handler_that_errors
    try:
        handler(None, mock_context)
    except:
        pass
    assert iopipe.report.errors['name'] == 'ValueError'
    assert iopipe.report.errors['message'] == 'Behold, a value error'


# Advanced reporting
@pytest.fixture
def advanced_handler(iopipe):
    nested_iopipe = []

    @iopipe.decorator
    def _advanced_handler(event, context):
        nested_iopipe.append(IOpipe('test-suite'))
        timestamp = time.time()
        report = nested_iopipe[0].create_report(timestamp, context)
        try:
            pass
        except Exception as e:
            nested_iopipe[0].err(e)
        report.update_data(context, timestamp)
        report.send()

    return nested_iopipe, _advanced_handler


def test_advanced_reporting(advanced_handler):

    mock_context = MockContext('advancedHandler', '1')
    nested_iopipe, handler = advanced_handler
    handler(None, mock_context)
    assert nested_iopipe[0].report.aws['functionName'] == 'advancedHandler'


@pytest.fixture
def advanced_handler_with_error(iopipe):
    nested_iopipe = []

    @iopipe.decorator
    def _advanced_handler_with_error(event, context):
        nested_iopipe.append(IOpipe('test-suite2'))
        timestamp = time.time()
        report = nested_iopipe[0].create_report(timestamp, context)
        nested_iopipe[0].log('name', 'foo')
        try:
            raise TypeError('Type error raised!')
        except Exception as e:
            nested_iopipe[0].err(e)
        report.send()

    return nested_iopipe, _advanced_handler_with_error


def test_advanced_erroring(advanced_handler_with_error, mock_context):

    mock_context = MockContext('advancedHandler', '1')
    nested_iopipe, handler = advanced_handler_with_error
    try:
        handler(None, mock_context)
    except Exception:
        pass
    assert nested_iopipe[0].report.errors['name'] == 'TypeError'
    assert nested_iopipe[0].report.errors['message'] == 'Type error raised!'
