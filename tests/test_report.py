import os

from iopipe.report import Report


def test_report_linux_system_success(iopipe, mock_context, assert_valid_schema):
    """Asserts that fields collected by the system module are present in a success report"""
    report = Report(iopipe, mock_context)
    report.prepare()

    assert_valid_schema(
        report.report,
        optional_fields=[
            "clientId",
            "dbTraceEntries",
            "environment.runtime.vendor",
            "environment.runtime.vmVendor",
            "environment.runtime.vmVersion",
            "environment.nodejs",
            "errors.count",
            "errors.message",
            "errors.name",
            "errors.stack",
            "errors.stackHash",
            "eventType",
            "labels",
            "memory",
            "projectId",
            "performanceEntries",
        ],
    )


def test_report_linux_system_error(iopipe, mock_context, assert_valid_schema):
    """Asserts that fields collected by the system module are present in a error report"""
    report = Report(iopipe, mock_context)

    try:
        raise Exception("Uh oh, this happened")
    except Exception as e:
        report.prepare(e)

    assert_valid_schema(
        report.report,
        optional_fields=[
            "clientId",
            "dbTraceEntries",
            "environment.runtime.vendor",
            "environment.runtime.vmVendor",
            "environment.runtime.vmVersion",
            "environment.nodejs",
            "errors.count",
            "errors.stackHash",
            "eventType",
            "labels",
            "memory",
            "projectId",
            "performanceEntries",
        ],
    )


def test_report_samlocal(monkeypatch, iopipe, mock_context):
    """Assert that if invoked by sam local that the function name is overridden"""
    monkeypatch.setattr(os, "environ", {"AWS_SAM_LOCAL": True})

    report = Report(iopipe, mock_context)
    report.prepare()

    assert (
        report.report["aws"]["invokedFunctionArn"]
        == "arn:aws:lambda:local:0:function:handler"
    )
