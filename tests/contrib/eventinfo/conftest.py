import json
import os
import pytest

from iopipe import IOpipeCore
from iopipe.contrib.eventinfo import EventInfoPlugin


@pytest.fixture
def iopipe_with_eventinfo():
    plugin = EventInfoPlugin()
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def handler_with_eventinfo(iopipe_with_eventinfo):
    @iopipe_with_eventinfo
    def _handler(event, context):
        pass

    return iopipe_with_eventinfo, _handler


@pytest.fixture
def handler_step_function_with_eventinfo(iopipe_with_eventinfo):
    @iopipe_with_eventinfo.step
    def _handler(event, context):
        assert context.iopipe.is_step_function is True
        return {}

    return iopipe_with_eventinfo, _handler


@pytest.fixture
def handler_http_response_with_eventinfo(iopipe_with_eventinfo):
    @iopipe_with_eventinfo
    def _handler(event, context):
        return {"statusCode": 200, "body": "success"}

    return iopipe_with_eventinfo, _handler


def _load_event(name):
    json_file = os.path.join(os.path.dirname(__file__), "events", "%s.json" % name)
    with open(json_file) as f:
        event = json.load(f)
    return event


@pytest.fixture
def event_alb():
    return _load_event("alb")


@pytest.fixture
def event_alexa_skill():
    return _load_event("alexa_skill")


@pytest.fixture
def event_apigw():
    return _load_event("apigw")


@pytest.fixture
def event_cloudfront():
    return _load_event("cloudfront")


@pytest.fixture
def event_kinesis():
    return _load_event("kinesis")


@pytest.fixture
def event_ses():
    return _load_event("ses")


@pytest.fixture
def event_sns():
    return _load_event("sns")


@pytest.fixture
def event_sqs():
    return _load_event("sqs")


@pytest.fixture
def event_scheduled():
    return _load_event("scheduled")


@pytest.fixture
def event_serverless_lambda():
    return _load_event("serverless_lambda")
