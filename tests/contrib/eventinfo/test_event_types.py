from iopipe.contrib.eventinfo import event_types as et
from iopipe.contrib.eventinfo.util import get_value


def test__event_types__alexa_skill(event_alexa_skill):
    event = et.AlexaSkill(event_alexa_skill)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}
    assert all([k.startswith('@iopipe/event-info.alexaSkill.') for k in event_info])
    assert len(list(event_info.keys())) == 31


def test__event_types__apigw(event_apigw):
    event = et.ApiGateway(event_apigw)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ['@iopipe/event-info.eventType'] + ['@iopipe/event-info.apiGateway.%s' % key for key in event.keys]
    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__event_types__cloudfront(event_cloudfront):
    event = et.CloudFront(event_cloudfront)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ['@iopipe/event-info.eventType'] + ['@iopipe/event-info.cloudFront.%s' % key for key in event.keys]
    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__event_types__kinesis(event_kinesis):
    event = et.Kinesis(event_kinesis)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ['@iopipe/event-info.eventType'] + ['@iopipe/event-info.kinesis.%s' % key for key in event.keys]
    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__event_types__scheduled(event_scheduled):
    event = et.Scheduled(event_scheduled)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ['@iopipe/event-info.eventType'] + ['@iopipe/event-info.scheduled.%s' % key for key in event.keys]
    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__event_types__serverless_lambda(event_serverless_lambda):
    event = et.ServerlessLambda(event_serverless_lambda)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = [
        '@iopipe/event-info.eventType',
        '@iopipe/event-info.eventType.source',
    ] + ['@iopipe/event-info.apiGateway.%s' % key[1] for key in event.keys]
    assert list(event_info.keys()).sort() == expected_keys.sort()
    assert all([
        get_value(event_serverless_lambda, old_key) == event_info['@iopipe/event-info.apiGateway.%s' % new_key]
        for old_key, new_key in event.keys
    ])
    assert event_info['@iopipe/event-info.eventType.source'] == event.source
