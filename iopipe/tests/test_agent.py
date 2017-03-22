from iopipe.iopipe import IOpipe
from .MockContext import MockContext
import time
global advancedUsage
global advancedUsageErr

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
    assert iopipe.report.client_id == 'test-suite'


def test_function_name_from_context():
    assert iopipe.report.aws['functionName'] == 'handler'


def test_custom_metrics():
    handlerWithEvents(None, context)
    assert len(iopipe.report.custom_metrics) == 2


def test_erroring():
    try:
        handlerThatErrors(None, context)
    except:
        pass
    assert iopipe.report.errors['name'] == 'ValueError'
    assert iopipe.report.errors['message'] == 'Behold, a value error'


# Advanced reporting
def advancedHandler(event, context):
    # make reference for testing
    global advancedUsage
    iopipe = IOpipe('test-suite')
    advancedUsage = iopipe
    timestamp = time.time()
    iopipe.start_report(timestamp, context)
    try:
        pass
    except Exception as e:
        iopipe.err(e)
    iopipe.send()


def test_advanced_reporting():
    new_context = MockContext('advancedHandler', '1')
    advancedHandler(None, new_context)
    assert(advancedUsage.report.aws['functionName']) == 'advancedHandler'


def advancedHandlerWithErr(event, context):
    global advancedUsageErr
    iopipe = IOpipe('test-suite2')
    advancedUsageErr = iopipe
    timestamp = time.time()
    iopipe.start_report(timestamp, context)
    iopipe.log('name', 'foo')
    try:
        raise TypeError('Type error raised!')
    except Exception as e:
        iopipe.err(e)
    iopipe.send()


def test_advanced_erroring():
    try:
        advancedHandlerWithErr(None, context)
    except:
        pass
    assert advancedUsageErr.report.errors['name'] == 'TypeError'
    assert advancedUsageErr.report.errors['message'] == 'Type error raised!'
