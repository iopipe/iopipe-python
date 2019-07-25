import json
import mock
import numbers
import time
from decimal import Decimal

import requests
import pytest

from iopipe import IOpipe, IOpipeCore
from iopipe.compat import string_types
from iopipe.contrib.trace import TracePlugin

SCHEMA_JSON = None
SCHEMA_JSON_URL = (
    "https://raw.githubusercontent.com/iopipe/iopipe/master/src/schema.json"
)


class MockContext(object):
    aws_request_id = "0"
    log_group_name = "mock-group"
    log_stream_name = "mock-stream"
    memory_limit_in_mb = 500

    def __init__(self, name="handler", version="$LATEST"):
        self.function_name = name
        self.function_version = version
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:1:function:%s:%s" % (
            name,
            version,
        )
        self.remaining_time_in_millis = float("inf")
        self.iopipe = mock.Mock()

    def get_remaining_time_in_millis(self):
        return self.remaining_time_in_millis

    def set_remaining_time_in_millis(self, time_remaining):
        self.remaining_time_in_millis = time_remaining


def _assert_valid_schema(obj, schema=None, path=None, optional_fields=None):
    """Asserts that an object matches the schema"""
    global SCHEMA_JSON

    if not schema:
        if not SCHEMA_JSON:
            r = requests.get(SCHEMA_JSON_URL)
            SCHEMA_JSON = json.loads(r.content)
        schema = SCHEMA_JSON

    if not path:
        path = []

    if not optional_fields:
        optional_fields = []

    if isinstance(obj, dict):
        for key in obj:
            key_path = ".".join(path + [key])
            assert key in schema, "%s not in schema" % key_path

    for key in schema:
        key_path = ".".join(path + [key])

        if key_path not in optional_fields:
            assert key in obj, "%s is required" % key_path

        if key not in obj:
            continue

        if isinstance(obj[key], dict):
            _assert_valid_schema(obj[key], schema[key], path + [key], optional_fields)
        elif isinstance(obj[key], list):
            for item in obj[key]:
                if isinstance(item, dict):
                    _assert_valid_schema(
                        item, schema[key][0], path + [key], optional_fields
                    )
        elif schema[key] == "b":
            assert isinstance(obj[key], bool), "%s not a boolean" % key_path
        elif schema[key] == "i":
            assert isinstance(obj[key], int), "%s not a integer" % key_path
        elif schema[key] == "n":
            assert isinstance(obj[key], numbers.Number), "%s not a number" % key_path
        elif schema[key] == "s":
            assert isinstance(obj[key], string_types), "%s not a string" % key_path


@pytest.fixture
def assert_valid_schema():
    return _assert_valid_schema


@pytest.fixture
def iopipe():
    return IOpipeCore("test-suite", "https://metrics-api.iopipe.com", True)


@pytest.fixture
def default_iopipe():
    return IOpipe("test-suite", "https://metrics-api.iopipe.com", True)


@pytest.fixture
def default_iopipe_override():
    return IOpipe(
        "test-suite",
        "https://metrics-api.iopipe.com",
        True,
        plugins=[TracePlugin(auto_measure=False)],
    )


@pytest.fixture
def iopipe_with_sync_http():
    return IOpipe("test-suite", "https://metrics-api.iopipe.com", True, sync_http=True)


@pytest.fixture
def mock_context():
    return MockContext("handler", "$LATEST")


@pytest.fixture
def handler(iopipe):
    @iopipe
    def _handler(event, context):
        pass

    return iopipe, _handler


@pytest.fixture
def handler_with_events(iopipe):
    @iopipe
    def _handler_with_events(event, context):
        iopipe.log("key1", 2)
        iopipe.log("key2", "qualitative value")
        context.iopipe.log("key3", 3)
        context.iopipe.log("key4", "second qualitative value")
        context.iopipe.metric("key5", 4)
        context.iopipe.metric("key6", "third qualitative value")
        context.iopipe.metric("key7", Decimal(12.3))
        context.iopipe.metric("a" * 129, "this will be dropped")

    return iopipe, _handler_with_events


@pytest.fixture
def handler_with_labels(iopipe):
    @iopipe
    def _handler_with_labels(event, context):
        context.iopipe.label("a-label")
        context.iopipe.label("a-label")  # duplicates are dropped
        context.iopipe.label("foo", "bar", "baz")  # multiple labels at once
        context.iopipe.label(u"another-label")  # works with unicode
        # These will be dropped
        context.iopipe.label(22)
        context.iopipe.label("a" * 129)  # too long

    return iopipe, _handler_with_labels


@pytest.fixture
def handler_that_errors(iopipe):
    @iopipe
    def _handler_that_errors(event, context):
        raise ValueError("Behold, a value error")

    return iopipe, _handler_that_errors


@pytest.fixture
def handler_that_timeouts(iopipe):
    @iopipe
    def _handler_that_timeouts(event, context):
        time.sleep(1)
        raise Exception("Should timeout before this is raised")

    return iopipe, _handler_that_timeouts


@pytest.fixture
def handler_with_sync_http(iopipe_with_sync_http):
    @iopipe_with_sync_http
    def _handler(event, context):
        pass

    return iopipe_with_sync_http, _handler


@pytest.fixture
def handler_that_disables_reporting(iopipe):
    @iopipe
    def _handler_that_disables_reporting(event, context):
        context.iopipe.disable()

    return iopipe, _handler_that_disables_reporting


@pytest.fixture
def handler_that_disables_reporting_with_error(iopipe):
    @iopipe
    def _handler_that_disables_reporting_with_error(event, context):
        context.iopipe.disable()
        raise Exception("An error happened")

    return iopipe, _handler_that_disables_reporting_with_error


@pytest.fixture
def handler_step_function(iopipe):
    @iopipe
    def _handler_not_step_function(event, context):
        assert context.iopipe.is_step_function is False

    @iopipe.step
    def _handler_step_function(event, context):
        assert context.iopipe.is_step_function is True

    return iopipe, _handler_step_function
