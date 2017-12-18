import os
import sys
import time

from iopipe import IOpipe

iopipe = IOpipe(os.getenv('IOPIPE_TOKEN'))


@iopipe
def caught_exception(event, context):
    try:
        raise Exception('Caught exception')
    except Exception as e:
        iopipe.error(e)


@iopipe
def coldstart(event, context):
    sys.exit(1)


@iopipe
def custom_metrics(event, context):
    iopipe.log('time', time.time())


@iopipe
def success(event, context):
    return {'message': 'Invocation success'}


@iopipe
def timeout(event, context):
    time.sleep(4)
    return {'message': 'Invocation success'}


@iopipe
def uncaught_exception(event, context):
    raise Exception('Invocation uncaught exception')
