import json
import os
import sys
import time

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from iopipe import IOpipe
from iopipe.contrib.eventinfo import EventInfoPlugin
from iopipe.contrib.logger import LoggerPlugin
from iopipe.contrib.profiler import ProfilerPlugin
from iopipe.contrib.trace import TracePlugin

iopipe = IOpipe(debug=True)
eventinfo_plugin = EventInfoPlugin()
iopipe_with_eventinfo = IOpipe(debug=True, plugins=[eventinfo_plugin])

logger_plugin = LoggerPlugin()
iopipe_with_logging = IOpipe(debug=True, plugins=[logger_plugin])

profiler_plugin = ProfilerPlugin(enabled=True)
iopipe_with_profiling = IOpipe(debug=True, plugins=[profiler_plugin])

trace_plugin = TracePlugin()
iopipe_with_tracing = IOpipe(debug=True, plugins=[trace_plugin])


@iopipe_with_eventinfo
def api_gateway(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({'success': True}),
    }


@iopipe_with_eventinfo
def api_trigger(event, context):
    gateway_url = os.getenv('PY_API_GATEWAY_URL')
    context.iopipe.metric('gateway_url', gateway_url or '')
    if gateway_url is not None:
        with urlopen(gateway_url) as r:
            context.iopipe.metric('response_status', getattr(r, 'status', getattr(r, 'code')))


def baseline(event, context):
    pass


def baseline_coldstart(event, context):
    sys.exit(1)


@iopipe
def caught_error(event, context):
    try:
        raise Exception('Caught exception')
    except Exception as e:
        context.iopipe.error(e)


@iopipe
def coldstart(event, context):
    sys.exit(1)


@iopipe
def custom_metrics(event, context):
    context.iopipe.metric('time', time.time())
    context.iopipe.metric('a-metric', 'value')
    context.iopipe.label('has-metrics')


@iopipe_with_logging
def logging(event, context):
    # This should still work (backwards compatibility)
    context.iopipe.log('time', time.time())

    context.iopipe.log.debug("I'm a debug message.")
    context.iopipe.log.info("I'm an info message.")
    context.iopipe.log.warn("I'm a warning message.")
    context.iopipe.log.error("I'm an error message.")
    context.iopipe.log.critical("I'm a critical message.")

    try:
        raise ValueError('I have no values.')
    except Exception as e:
        context.log.exception(e)


def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


@iopipe_with_profiling
def profiling(event, context):
    fib_number = fib(10)
    context.iopipe.metric('fib number', fib_number)


@iopipe
def success(event, context):
    return {'message': 'Invocation successful'}


@iopipe
def timeout(event, context):
    time.sleep(2)
    return {'message': 'Invocation success'}


@iopipe_with_tracing
def tracing(event, context):
    context.iopipe.mark.start('foobar')
    time.sleep(1)
    context.iopipe.mark.end('foobar')


@iopipe
def uncaught_error(event, context):
    raise Exception('Invocation uncaught exception')
