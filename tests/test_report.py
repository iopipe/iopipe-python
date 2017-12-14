import sys

import mock
import pytest

from iopipe.config import set_config
from iopipe.report import Report

from .mock_context import MockContext
from .util import assert_valid_schema


@mock.patch('iopipe.report.send_report')
def test_report_linux_system_success(mock_send_report):
    """Asserts that fields collected by the system module are present in a success report"""
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    mock_context = MockContext()

    report = Report(set_config(), mock_context)
    report.send()

    assert_valid_schema(report.report, optional_fields=[
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


@mock.patch('iopipe.report.send_report')
def test_report_linux_system_error(mock_send_report):
    """Asserts that fields collected by the system module are present in a error report"""
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    mock_context = MockContext()

    report = Report(set_config(), mock_context)

    try:
        raise Exception('Uh oh, this happened')
    except Exception as e:
        report.send(e)

    assert_valid_schema(report.report, optional_fields=[
        'aws.traceId',
        'environment.nodejs',
        'errors.count',
        'errors.stackHash',
        'memory',
        'projectId',
        'performanceEntries',
    ])
