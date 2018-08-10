import copy
import json
import logging
import os
import platform
import sys
import time
import traceback

from . import constants
from .monotonic import monotonic
from .plugins import get_plugin_meta
from .send_report import send_report

if sys.platform.startswith("linux"):
    from . import system
else:
    from . import mock_system as system

logger = logging.getLogger(__name__)


class Report(object):
    """
    The report of system status
    """

    def __init__(self, client, context):
        """
        Instantiates a new IOpipe report.

        :param client: The IOpipe client.
        :param context: The AWS Lambda context.
        """
        self.start_time = monotonic()
        self.sent = False
        self.stat_start = system.read_pid_stat("self")

        self.client = client
        self.config = client.config
        self.context = context

        self.custom_metrics = []
        self.http_trace_entries = []
        self.labels = set()
        self.performance_entries = []
        self.plugins = get_plugin_meta(self.config["plugins"])

        self.report = {
            "client_id": self.config["token"],
            "coldstart": constants.COLDSTART,
            "custom_metrics": self.custom_metrics,
            "environment": {
                "agent": {
                    "load_time": constants.MODULE_LOAD_TIME,
                    "runtime": "python",
                    "version": constants.VERSION,
                },
                "runtime": {
                    "name": platform.python_implementation(),
                    "version": platform.python_version(),
                },
                # DEPRECATED: the following key will be removed in favor of
                # the 'runtime' in the future
                "python": {"version": platform.python_version()},
                "host": {},
                "os": {"linux": {}},
            },
            "errors": {},
            "httpTraceEntries": self.http_trace_entries,
            "installMethod": self.config.get("install_method"),
            "performanceEntries": self.performance_entries,
            "plugins": self.plugins,
            "processId": constants.PROCESS_ID,
            "timestamp": int(time.time() * 1000),
        }

        if constants.COLDSTART is True:
            constants.COLDSTART = False
            self.labels.add("@iopipe/coldstart")

    def extract_context_data(self):
        """
        Returns the contents of a AWS Lambda context.

        :returns: A dict of relevant context data.
        :rtype: dict
        """
        data = {}
        for k, v in {
            # camel case names in the report to align with AWS standards
            "functionName": "function_name",
            "functionVersion": "function_version",
            "memoryLimitInMB": "memory_limit_in_mb",
            "invokedFunctionArn": "invoked_function_arn",
            "awsRequestId": "aws_request_id",
            "logGroupName": "log_group_name",
            "logStreamName": "log_stream_name",
        }.items():
            if hasattr(self.context, v):
                data[k] = getattr(self.context, v)
        if (
            hasattr(self.context, "invoked_function_arn")
            and "AWS_SAM_LOCAL" in os.environ
        ):
            data["invokedFunctionArn"] = (
                "arn:aws:lambda:local:0:function:%s"
                % data.get("functionName", "unknown")
            )
        if hasattr(self.context, "get_remaining_time_in_millis") and callable(
            self.context.get_remaining_time_in_millis
        ):
            data[
                "getRemainingTimeInMillis"
            ] = self.context.get_remaining_time_in_millis()
        data["traceId"] = os.getenv("_X_AMZN_TRACE_ID", "")
        return data

    def retain_error(self, error, frame=None):
        """
        Adds details of an error to the report.

        :param error: The error exception to add to the report.
        """
        if frame is None:
            stack = traceback.format_exc()
            self.labels.add("@iopipe/error")
        else:
            stack = "\n".join(traceback.format_stack(frame))
            self.labels.add("@iopipe/timeout")
        details = {
            "name": type(error).__name__,
            "message": "{}".format(error),
            "stack": stack,
        }
        self.report["errors"] = details

    def prepare(self, error=None, frame=None):
        """
        Prepare the report to be sent to IOpipe.

        :param error: An optional error to add to report.
        :param frame: A stack frame to add to report in the event of a timeout.
        """
        if error:
            self.retain_error(error, frame)

        self.report["environment"]["host"]["boot_id"] = system.read_bootid()

        # convert labels to list for sending
        self.report["labels"] = list(self.labels)

        meminfo = system.read_meminfo()

        self.report.update(
            {
                "aws": self.extract_context_data(),
                "timestampEnd": int(time.time() * 1000),
            }
        )

        self.report["environment"]["os"].update(
            {
                "cpus": system.read_stat(),
                "freemem": meminfo["MemFree"],
                "hostname": system.read_hostname(),
                "totalmem": meminfo["MemTotal"],
                "usedmem": meminfo["MemTotal"] - meminfo["MemFree"],
            }
        )

        self.report["environment"]["os"]["linux"]["pid"] = {
            "self": {
                "stat": system.read_pid_stat("self"),
                "stat_start": self.stat_start,
                "status": system.read_pid_status("self"),
            }
        }

        self.report["disk"] = system.read_disk()

        self.report["duration"] = int((monotonic() - self.start_time) * 1e9)

    def send(self):
        """
        Sends the report to IOpipe.
        """
        if self.sent is True:
            return
        self.sent = True

        logger.debug("Sending report to IOpipe:")
        logger.debug(json.dumps(self.report, indent=2, sort_keys=True))

        self.client.submit_future(send_report, copy.deepcopy(self.report), self.config)
