import mock
import os

from iopipe.contrib.eventinfo import EventInfoPlugin


@mock.patch("iopipe.report.send_report", autospec=True)
def test__eventinfo_plugin__apigw(
    mock_send_report, handler_with_eventinfo, event_apigw, mock_context
):
    iopipe, handler = handler_with_eventinfo
    plugins = iopipe.config["plugins"]

    assert len(plugins) == 1
    assert plugins[0].enabled is True
    assert plugins[0].name == "event-info"

    handler(event_apigw, mock_context)
    metrics = iopipe.report.custom_metrics

    assert any([m["name"] == "@iopipe/event-info.eventType" for m in metrics])
    assert len(metrics) == 10
    assert "@iopipe/plugin-event-info" in iopipe.report.labels
    assert "@iopipe/aws-api-gateway" in iopipe.report.labels

    event_type = [m for m in metrics if m["name"] == "@iopipe/event-info.eventType"]
    assert len(event_type) == 1
    assert event_type[0]["s"] == "apiGateway"

    assert "eventType" in iopipe.report.report
    assert iopipe.report.report["eventType"] == "aws-api-gateway"


@mock.patch("iopipe.report.send_report", autospec=True)
def test__eventinfo_plugin__cloudfront(
    mock_send_report, handler_with_eventinfo, event_cloudfront, mock_context
):
    iopipe, handler = handler_with_eventinfo
    plugins = iopipe.config["plugins"]

    assert len(plugins) == 1
    assert plugins[0].enabled is True
    assert plugins[0].name == "event-info"

    handler(event_cloudfront, mock_context)
    metrics = iopipe.report.custom_metrics

    assert any([m["name"] == "@iopipe/event-info.eventType" for m in metrics])
    assert len(metrics) == 7

    event_type = [m for m in metrics if m["name"] == "@iopipe/event-info.eventType"]
    assert len(event_type) == 1
    assert event_type[0]["s"] == "cloudFront"

    assert "eventType" in iopipe.report.report
    assert iopipe.report.report["eventType"] == "aws-cloud-front"


@mock.patch("iopipe.report.send_report", autospec=True)
def test__eventinfo_plugin__kinesis(
    mock_send_report, handler_with_eventinfo, event_kinesis, mock_context
):
    iopipe, handler = handler_with_eventinfo
    plugins = iopipe.config["plugins"]

    assert len(plugins) == 1
    assert plugins[0].enabled is True
    assert plugins[0].name == "event-info"

    handler(event_kinesis, mock_context)
    metrics = iopipe.report.custom_metrics

    assert any([m["name"] == "@iopipe/event-info.eventType" for m in metrics])
    assert len(metrics) == 4

    event_type = [m for m in metrics if m["name"] == "@iopipe/event-info.eventType"]
    assert len(event_type) == 1
    assert event_type[0]["s"] == "kinesis"

    assert "eventType" in iopipe.report.report
    assert iopipe.report.report["eventType"] == "aws-kinesis"


@mock.patch("iopipe.report.send_report", autospec=True)
def test__eventinfo_plugin__scheduled(
    mock_send_report, handler_with_eventinfo, event_scheduled, mock_context
):
    iopipe, handler = handler_with_eventinfo
    plugins = iopipe.config["plugins"]

    assert len(plugins) == 1
    assert plugins[0].enabled is True
    assert plugins[0].name == "event-info"

    handler(event_scheduled, mock_context)
    metrics = iopipe.report.custom_metrics

    assert any([m["name"] == "@iopipe/event-info.eventType" for m in metrics])
    assert len(metrics) == 6

    event_type = [m for m in metrics if m["name"] == "@iopipe/event-info.eventType"]
    assert len(event_type) == 1
    assert event_type[0]["s"] == "scheduled"

    assert "eventType" in iopipe.report.report
    assert iopipe.report.report["eventType"] == "aws-scheduled"


def test__eventinfo_plugin__enabled(monkeypatch):
    monkeypatch.setattr(os, "environ", {"IOPIPE_EVENT_INFO_ENABLED": "true"})

    plugin = EventInfoPlugin(enabled=False)

    assert plugin.enabled is True


@mock.patch("iopipe.report.send_report", autospec=True)
def test__eventinfo_plugin__step_function(
    mock_send_report, handler_step_function_with_eventinfo, event_apigw, mock_context
):
    iopipe, handler = handler_step_function_with_eventinfo

    plugins = iopipe.config["plugins"]
    assert len(plugins) == 1
    assert plugins[0].enabled is True
    assert plugins[0].name == "event-info"

    response1 = handler(event_apigw, mock_context)
    assert "iopipe" in response1
    assert "id" in response1["iopipe"]
    assert "step" in response1["iopipe"]

    response2 = handler(response1, mock_context)

    assert "iopipe" in response2
    assert response1["iopipe"]["id"] == response2["iopipe"]["id"]
    assert response2["iopipe"]["step"] > response1["iopipe"]["step"]


@mock.patch("iopipe.report.send_report", autospec=True)
def test__eventinfo_plugin__http_response(
    mock_send_report, handler_http_response_with_eventinfo, event_apigw, mock_context
):
    iopipe, handler = handler_http_response_with_eventinfo

    handler(event_apigw, mock_context)
    metrics = iopipe.report.custom_metrics

    assert any(
        (
            m["name"] == "@iopipe/event-info.apiGateway.response.statusCode"
            for m in metrics
        )
    )
    assert all(
        (
            "n" in m
            for m in metrics
            if m["name"] == "@iopipe/event-info.apiGateway.response.statusCode"
        )
    )

    metric = next(
        (
            m
            for m in metrics
            if m["name"] == "@iopipe/event-info.apiGateway.response.statusCode"
        )
    )
    assert metric["n"] == 200
