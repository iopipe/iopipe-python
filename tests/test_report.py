import json
import numbers
import sys

import mock
import pytest
import requests

from iopipe.config import set_config
from iopipe.report import Report

from .mock_context import MockContext

SCHEMA_JSON_URL = 'https://raw.githubusercontent.com/iopipe/iopipe/master/src/schema.json'


def assert_valid_schema(obj, schema=None, path=None, optional_fields=None):
    """Asserts that an object matches the schema"""

    if not schema:
        r = requests.get(SCHEMA_JSON_URL)
        schema = json.loads(r.content)

    if not path:
        path = []

    if not optional_fields:
        optional_fields = []

    for key in schema:
        key_path = '.'.join(path + [key])

        if key_path not in optional_fields:
            assert key in obj, '%s is required' % key_path

        if key not in obj:
            continue

        if isinstance(obj[key], dict):
            assert_valid_schema(obj[key], schema[key], path + [key], optional_fields)
        elif isinstance(obj[key], list):
            for item in obj[key]:
                assert_valid_schema(item, schema[key][0], path + [key], optional_fields)
        elif schema[key] == 'b':
            assert isinstance(obj[key], bool), '%s not a boolean' % key_path
        elif schema[key] == 'i':
            assert isinstance(obj[key], int), '%s not a integer' % key_path
        elif schema[key] == 'n':
            assert isinstance(obj[key], numbers.Number), '%s not a number' % key_path
        elif schema[key] == 's':
            assert isinstance(obj[key], str), '%s not a string' % key_path


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
        'timestampEnd',
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
        'timestampEnd',
    ])
