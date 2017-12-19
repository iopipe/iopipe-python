import os
import sys
import time

from iopipe import IOpipe
from iopipe.contrib.trace import TracePlugin

iopipe = IOpipe(os.getenv('IOPIPE_TOKEN'))

trace_plugin = TracePlugin()
iopipe_with_tracing = IOpipe(os.getenv('IOPIPE_TOKEN'), plugins=[trace_plugin])


@iopipe
def caught_exception(event, context):
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


@iopipe
def success(event, context):
    return {'message': 'Invocation successful'}


@iopipe
def timeout(event, context):
    time.sleep(4)
    return {'message': 'Invocation success'}


@iopipe_with_tracing
def tracing(event, context):
    context.iopipe.mark.start('foobar')
    time.sleep(1)
    context.iopipe.mark.end('foobar')
    context.iopipe.mark.measure('foobar')


@iopipe
def uncaught_exception(event, context):
    raise Exception('Invocation uncaught exception')
