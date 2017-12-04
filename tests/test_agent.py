import pytest

from iopipe import constants, IOpipe

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


def test_coldstarts(handler, mock_context, monkeypatch):
    monkeypatch.setattr(constants, 'COLDSTART', True)

    iopipe, handler = handler

    handler(None, mock_context)
    assert iopipe.report.report['coldstart'] is True

    handler(None, mock_context)
    assert iopipe.report.report['coldstart'] is False


def test_client_id_is_configured(handler, mock_context):
    iopipe, handler = handler
    handler(None, mock_context)
    assert iopipe.report.report['client_id'] == 'test-suite'


def test_function_name_from_context(handler, mock_context):
    iopipe, handler = handler
    handler(None, mock_context)
    assert iopipe.report.report['aws']['functionName'] == 'handler'


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
    assert iopipe.report.report['errors']['name'] == 'ValueError'
    assert iopipe.report.report['errors']['message'] == 'Behold, a value error'
