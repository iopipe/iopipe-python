import logging
import pytest

from iopipe import IOpipe
from iopipe.contrib.logging import LoggingPlugin

logger = logging.getLogger('testlog')
logger.setLevel(logging.DEBUG)


@pytest.fixture
def iopipe_with_logging():
    plugin = LoggingPlugin(name='testlog')
    return IOpipe(token='test-suite', url='https://metrics-api.iopipe.com', debug=True, plugins=[plugin])


@pytest.fixture
def handler_with_logging(iopipe_with_logging):
    @iopipe_with_logging
    def _handler(event, context):
        logger.debug('I got nothing.')
        logger.info('I might have something.')
        logger.warn('Got something.')
        logger.error('And you have it, too.')
        logger.critical("And it's fatal.")

    return iopipe_with_logging, _handler
