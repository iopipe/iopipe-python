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


@iopipe.decorator
def handlerThatErrors(event, context):
    raise ValueError("Behold, a value error")


def setup_function():
    handler(None, context)


def test_client_id_is_configured():
    assert iopipe.report['client_id'] == 'test-suite'


def test_function_name_from_context():
    assert iopipe.report['aws']['functionName'] == 'handler'


def test_custom_metrics():
    handlerWithEvents(None, context)
    # custom metrics are cleared after an invocations
    # TODO modify reporting scheme so we can inspect metrics
    assert len(iopipe.report['custom_metrics']) == 0

# TODO: update report so report can be inpected (same note as custom metrics)
# def test_erroring():
#     try:
#         handlerThatErrors(None, context)
#     except:
#         pass
#     assert iopipe.report['errors']['name'] == 'ValueError'
#     assert iopipe.report['errors']['message'] == 'Behold, a value error'
