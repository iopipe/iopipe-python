from iopipe.iopipe import IOpipe
from .MockContext import MockContext

iopipe = IOpipe('test-suite', 'https://metrics-api.iopipe.com', False)
context = MockContext('handler', '$LATEST')


@iopipe.decorator
def handler(event, context):
    pass


def setup_function():
    handler(None, context)


def test_client_id_is_configured():
    assert iopipe.report['client_id'] == 'test-suite'


def test_function_name_from_context():
    assert iopipe.report['aws']['functionName'] == 'handler'
