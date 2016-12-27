from iopipe.iopipe import IOpipe
from .MockContext import MockContext

iopipe = IOpipe('test-suite', 'https://metrics-api.iopipe.com', True)
context = MockContext('handler', '$LATEST')


@iopipe.decorator
def handler(event, context):
    pass


@iopipe.decorator
def handlerWithEvents(event, context):
    iopipe.log('somekey', 2)
    iopipe.log('anotherkey', 'qualitative value')


def setup_function():
    handler(None, context)


def test_client_id_is_configured():
    assert iopipe.report['client_id'] == 'test-suite'


def test_function_name_from_context():
    assert iopipe.report['aws']['functionName'] == 'handler'


def test_reporting_custom_metrics():
    handlerWithEvents(None, context)
    assert len(iopipe.report['custom_metrics']) == 2
    assert iopipe.report['custom_metrics'][0]['name'] == 'somekey'
