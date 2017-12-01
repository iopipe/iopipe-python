import mock
import pytest
import sys

from iopipe.config import set_config
from iopipe.report import Report

from .mock_context import MockContext


@mock.patch('iopipe.report.send_report')
def test_report_linux_system(mock_send_report):
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    mock_context = MockContext()

    report = Report(set_config(), mock_context)
    report.send()

    assert 'aws' in report.report

    for key in ['functionName', 'functionVersion', 'awsRequestId',
                'invokedFunctionArn', 'logGroupName', 'logStreamName',
                'memoryLimitInMB', 'getRemainingTimeInMillis']:
        assert key in report.report['aws']

    assert 'cpus' in report.report['environment']['os']

    for cpu in report.report['environment']['os']['cpus']:
        assert 'times' in cpu
        for key in ['idle', 'irq', 'sys', 'user', 'nice']:
            assert key in cpu['times']

    assert 'freemem' in report.report['environment']['os']
    assert 'totalmem' in report.report['environment']['os']

    for key in ['utime', 'stime', 'cutime', 'cstime', 'rss']:
        assert key in report.report['environment']['os']['linux']['pid']['self']['stat']
        assert key in report.report['environment']['os']['linux']['pid']['self']['stat_start']

    for key in ['VmRSS', 'Threads', 'FDSize']:
        assert key in report.report['environment']['os']['linux']['pid']['self']['status']
