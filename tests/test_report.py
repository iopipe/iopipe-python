from iopipe.config import set_config
from iopipe.report import Report


def test_report_linux_system_success(mock_context, assert_valid_schema):
    """Asserts that fields collected by the system module are present in a success report"""
    report = Report(set_config(), mock_context)
    report.prepare()

    assert_valid_schema(
        report.report,
        optional_fields=[
            'aws.traceId',
            'environment.nodejs',
            'errors.count',
            'errors.message',
            'errors.name',
            'errors.stack',
            'errors.stackHash',
            'memory',
            'projectId',
            'performanceEntries',
        ])


def test_report_linux_system_error(mock_context, assert_valid_schema):
    """Asserts that fields collected by the system module are present in a error report"""
    report = Report(set_config(), mock_context)

    try:
        raise Exception('Uh oh, this happened')
    except Exception as e:
        report.prepare(e)

    assert_valid_schema(
        report.report,
        optional_fields=[
            'aws.traceId',
            'environment.nodejs',
            'errors.count',
            'errors.stackHash',
            'memory',
            'projectId',
            'performanceEntries',
        ])
