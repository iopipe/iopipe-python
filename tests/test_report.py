import json
import numbers
import os
import sys

import mock
import pytest
import requests

from iopipe.config import set_config
from iopipe.report import Report

from .mock_context import MockContext

SCHEMA_JSON_URL = 'https://raw.githubusercontent.com/iopipe/iopipe/master/src/schema.json'


def assert_valid_schema(obj, schema=None, path=None):
    """Asserts that an object matches the schema"""

    if not schema:
        r = requests.get(SCHEMA_JSON_URL)
        schema = json.loads(r.content)

    if not path:
        path = []

    for key in obj:
        if key not in schema:
            continue

        if isinstance(obj[key], dict):
            assert_valid_schema(obj[key], schema[key], path + [key])
        elif isinstance(obj[key], list):
            for item in obj[key]:
                assert_valid_schema(item, schema[key][0], path + [key])
        elif schema[key] == 'b':
            assert isinstance(obj[key], bool), '%s not a boolean' % '.'.join(path + [key])
        elif schema[key] == 'i':
            assert isinstance(obj[key], int), '%s not a integer' % '.'.join(path + [key])
        elif schema[key] == 'n':
            assert isinstance(obj[key], numbers.Number), '%s not a number' % '.'.join(path + [key])
        elif schema[key] == 's':
            assert isinstance(obj[key], str), '%s not a string' % '.'.join(path + [key])


@mock.patch('iopipe.report.send_report')
def test_report_linux_system(mock_send_report):
    """Asserts that fields collected by the system module are present in a report"""

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

    assert_valid_schema(report.report)
