from iopipe.contrib.eventinfo import event_types as et
from iopipe.contrib.eventinfo.util import collect_all_keys, get_value


def test__event_types__alb(event_alb):
    event = et.ALB(event_alb)

    assert event.has_required_keys() is True

    event_info = event.collect()
    expected_keys = ["@iopipe/event-info.eventType"] + [
        "@iopipe/event-info.alb.%s" % key for key in event.keys
    ]
    assert list(event_info.keys()).sort() == expected_keys.sort()
    assert len(list(event_info.keys())) == len(event.keys) + 1


def test__event_types__alexa_skill(event_alexa_skill):
    event = et.AlexaSkill(event_alexa_skill)
    assert event.has_required_keys() is True

    event_info = event.collect()
    expected_keys = ["@iopipe/event-info.eventType"] + [
        "@iopipe/event-info.alexaSkill.%s" % key for key in event.keys
    ]
    assert list(event_info.keys()).sort() == expected_keys.sort()
    assert len(list(event_info.keys())) == 32

    assert (
        "@iopipe/event-info.alexaSkill.context.System.user.accessToken"
        not in event_info
    )
    assert (
        "@iopipe/event-info.alexaSkill.context.System.user.permissions.consentToken"
        not in event_info
    )


def test__event_types__apigw(event_apigw):
    event = et.ApiGateway(event_apigw)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ["@iopipe/event-info.eventType"] + [
        "@iopipe/event-info.apiGateway.%s" % key for key in event.keys
    ]
    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__event_types__cloudfront(event_cloudfront):
    event = et.CloudFront(event_cloudfront)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ["@iopipe/event-info.eventType"] + [
        "@iopipe/event-info.cloudFront.%s" % key for key in event.keys
    ]
    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__event_types__kinesis(event_kinesis):
    event = et.Kinesis(event_kinesis)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ["@iopipe/event-info.eventType"] + [
        "@iopipe/event-info.kinesis.%s" % key for key in event.keys
    ]
    assert list(event_info.keys()).sort() == expected_keys.sort()

    assert isinstance(event_info["@iopipe/event-info.kinesis.Records.length"], int)


def test__event_types__scheduled(event_scheduled):
    event = et.Scheduled(event_scheduled)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ["@iopipe/event-info.eventType"] + [
        "@iopipe/event-info.scheduled.%s" % key for key in event.keys
    ]
    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__event_types__serverless_lambda(event_serverless_lambda):
    event = et.ServerlessLambda(event_serverless_lambda)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = [
        "@iopipe/event-info.eventType",
        "@iopipe/event-info.eventType.source",
    ] + ["@iopipe/event-info.apiGateway.%s" % key[1] for key in event.keys]
    assert list(event_info.keys()).sort() == expected_keys.sort()
    assert all(
        [
            get_value(event_serverless_lambda, old_key)
            == event_info["@iopipe/event-info.apiGateway.%s" % new_key]
            for old_key, new_key in event.keys
        ]
    )
    assert event_info["@iopipe/event-info.eventType.source"] == event.source


def test__event_types__ses(event_ses):
    event = et.SES(event_ses)

    assert event.has_required_keys() is True

    event_info = event.collect()

    assert event_info != {}

    expected_keys = ["@iopipe/event-info.eventType"] + [
        "@iopipe/event-info.ses.%s" % key for key in event.keys
    ]

    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__event_types__sns(event_sns):
    event = et.SNS(event_sns)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ["@iopipe/event-info.eventType"] + [
        "@iopipe/event-info.sns.%s" % key for key in event.keys
    ]
    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__event_types__sqs(event_sqs):
    event = et.SQS(event_sqs)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}

    expected_keys = ["@iopipe/event-info.eventType"] + [
        "@iopipe/event-info.sqs.%s" % key for key in event.keys
    ]
    assert list(event_info.keys()).sort() == expected_keys.sort()


def test__collect_all_keys__coerce_types():
    info = collect_all_keys(
        {"foo": {"bar": {"baz": "123", "boo": "wut?"}}},
        "@iopipe/event-info.test",
        ["foo.bar.boo"],
        {"foo.bar.baz": int},
    )

    assert "@iopipe/event-info.test.foo.bar.baz" in info
    assert "@iopipe/event-info.test.foo.bar.boo" not in info
    assert isinstance(info["@iopipe/event-info.test.foo.bar.baz"], int)
