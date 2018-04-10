import os

from iopipe.config import set_config
from iopipe.report import Report


def test_report_linux_system_success(mock_context, assert_valid_schema):
    """Asserts that fields collected by the system module are present in a success report"""
    report = Report(set_config(), mock_context)
    report.prepare()

    assert_valid_schema(
        report.report,
        optional_fields=[
            'disk',
            'environment.runtime.vendor',
            'environment.runtime.vmVendor',
            'environment.runtime.vmVersion',
            'environment.nodejs',
            'errors.count',
            'errors.message',
            'errors.name',
            'errors.stack',
            'errors.stackHash',
            'labels',
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
            'disk',
            'environment.runtime.vendor',
            'environment.runtime.vmVendor',
            'environment.runtime.vmVersion',
            'environment.nodejs',
            'errors.count',
            'errors.stackHash',
            'labels',
            'memory',
            'projectId',
            'performanceEntries',
        ])


def test_report_samlocal(monkeypatch, mock_context):
    """Assert that if invoked by sam local that the function name is overridden"""
    monkeypatch.setattr(os, 'environ', {'AWS_SAM_LOCAL': True})

    report = Report(set_config(), mock_context)
    report.prepare()

    assert report.report['aws']['invokedFunctionArn'] == 'arn:aws:lambda:local:0:function:handler'
