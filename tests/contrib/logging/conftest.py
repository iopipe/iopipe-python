from __future__ import print_function

import pytest

from iopipe import IOpipe
from iopipe.contrib.logging import LoggingPlugin


@pytest.fixture
def iopipe_with_logging():
    plugin = LoggingPlugin('testlog')
    return IOpipe(token='test-suite', url='https://metrics-api.iopipe.com', plugins=[plugin])


@pytest.fixture
def handler_with_logging(iopipe_with_logging):
    @iopipe_with_logging
    def _handler(event, context):
        context.iopipe.log.debug('I got nothing.')
        context.iopipe.log.info('I might have something.')
        context.iopipe.log.warn('Got something.')
        context.iopipe.log.error('And you have it, too.')
        context.iopipe.log.critical("And it's fatal.")

        print('This is not a misprint.')

    return iopipe_with_logging, _handler


@pytest.fixture
def iopipe_with_logging_debug():
    plugin = LoggingPlugin(name='testlog')
    return IOpipe(token='test-suite', url='https://metrics-api.iopipe.com', debug=True, plugins=[plugin])


@pytest.fixture
def handler_with_logging_debug(iopipe_with_logging_debug):
    @iopipe_with_logging_debug
    def _handler(event, context):
        context.iopipe.log.debug('I should be logged.')

    return iopipe_with_logging_debug, _handler
