import json
import os
import random
import sys
import time

try:
    from botocore.vendored import requests
except ImportError:
    import requests

from iopipe import IOpipe, IOpipeCore
from iopipe.contrib.eventinfo import EventInfoPlugin
from iopipe.contrib.logger import LoggerPlugin
from iopipe.contrib.profiler import ProfilerPlugin
from iopipe.contrib.trace import TracePlugin

iopipe = IOpipe(debug=True)

eventinfo_plugin = EventInfoPlugin()
iopipe_with_eventinfo = IOpipeCore(debug=True, plugins=[eventinfo_plugin])

logger_plugin = LoggerPlugin(enabled=True)
iopipe_with_logging = IOpipeCore(debug=True, plugins=[logger_plugin])

logger_plugin_tmp = LoggerPlugin(enabled=True, use_tmp=True)
iopipe_with_logging_tmp = IOpipeCore(debug=True, plugins=[logger_plugin_tmp])

profiler_plugin = ProfilerPlugin(enabled=True)
iopipe_with_profiling = IOpipeCore(debug=True, plugins=[profiler_plugin])

iopipe_with_sync_http = IOpipe(debug=True, sync_http=True)

trace_plugin = TracePlugin()
iopipe_with_tracing = IOpipeCore(debug=True, plugins=[trace_plugin])

trace_plugin_auto_http = TracePlugin(auto_http=True)
iopipe_with_auto_http = IOpipeCore(debug=True, plugins=[trace_plugin_auto_http])


@iopipe_with_eventinfo
def api_gateway(event, context):
    return {"statusCode": 200, "body": json.dumps({"success": True})}


@iopipe_with_auto_http
def api_trigger(event, context):
    gateway_url = os.getenv("PY_API_GATEWAY_URL")
    context.iopipe.metric("gateway_url", gateway_url or "")
    if gateway_url is not None:
        response = requests.get(gateway_url)
        context.iopipe.metric("response_status", response.status_code)


@iopipe_with_auto_http
def auto_http(event, context):
    requests.get("https://www.iopipe.com")


def baseline(event, context):
    pass


def baseline_coldstart(event, context):
    sys.exit(1)


@iopipe
def caught_error(event, context):
    try:
        raise Exception("Caught exception")
    except Exception as e:
        context.iopipe.error(e)


def coldstart(event, context):
    @iopipe
    def handler(event, context):
        pass

    handler(event, context)

    sys.exit(1)


@iopipe
def custom_metrics(event, context):
    context.iopipe.metric("time", time.time())
    context.iopipe.metric("a-metric", "value")
    context.iopipe.label("has-metrics")


@iopipe_with_logging
def logging(event, context):
    # This should still work (backwards compatibility)
    context.iopipe.log("time", time.time())

    print("I'm redirecting stdout")

    context.iopipe.log.debug("I'm a debug message.")
    context.iopipe.log.info("I'm an info message.")
    context.iopipe.log.warn("I'm a warning message.")
    context.iopipe.log.error("I'm an error message.")
    context.iopipe.log.critical("I'm a critical message.")

    try:
        raise ValueError("I have no values.")
    except Exception as e:
        context.iopipe.log.exception(e)


@iopipe_with_logging_tmp
def logging_tmp(event, context):
    with open("text.json") as f:
        text = json.load(f)

    for _ in range(1000):
        level = random.choice(["debug", "info", "warn", "error", "critical"])
        random_text = random.choice(text["text"])
        getattr(context.iopipe.log, level)(random_text)


def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


@iopipe_with_profiling
def profiling(event, context):
    fib_number = fib(10)
    context.iopipe.metric("fib number", fib_number)


@iopipe
def success(event, context):
    return {"message": "Invocation successful"}


@iopipe_with_sync_http
def sync_http(event, context):
    return {"message": "Invocation successful"}


@iopipe
def timeout(event, context):
    time.sleep(2)
    return {"message": "Invocation success"}


@iopipe_with_tracing
def tracing(event, context):
    context.iopipe.mark.start("foobar")
    time.sleep(1)
    context.iopipe.mark.end("foobar")


@iopipe
def uncaught_error(event, context):
    raise Exception("Invocation uncaught exception")
