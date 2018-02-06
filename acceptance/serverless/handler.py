import os
import sys
import time

from iopipe import IOpipe
from iopipe.contrib.profiler import ProfilerPlugin
from iopipe.contrib.trace import TracePlugin

iopipe = IOpipe(os.getenv('IOPIPE_TOKEN'))

profiler_plugin = ProfilerPlugin(enabled=True)
iopipe_with_profiling = IOpipe(os.getenv('IOPIPE_TOKEN'), plugins=[profiler_plugin])

trace_plugin = TracePlugin()
iopipe_with_tracing = IOpipe(os.getenv('IOPIPE_TOKEN'), plugins=[trace_plugin])


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
    context.iopipe.log('time', time.time())


@iopipe_with_profiling
def profiling(event, context):
    time.sleep(1)


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
    context.iopipe.mark.measure('foobar')


@iopipe
def uncaught_error(event, context):
    raise Exception('Invocation uncaught exception')
