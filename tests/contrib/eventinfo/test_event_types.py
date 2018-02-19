from iopipe.contrib.eventinfo import event_types as et


def test__event_Types__apigw(event_apigw):
    event = et.ApiGateway(event_apigw)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}


def test__event_Types__cloudfront(event_cloudfront):
    event = et.CloudFront(event_cloudfront)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}


def test__event_types__kinesis(event_kinesis):
    event = et.Kinesis(event_kinesis)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}


def test__event_types__scheduled(event_scheduled):
    event = et.Scheduled(event_scheduled)
    assert event.has_required_keys() is True

    event_info = event.collect()
    assert event_info != {}
