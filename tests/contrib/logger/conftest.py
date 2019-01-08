from __future__ import print_function

import pytest

from iopipe import IOpipeCore
from iopipe.contrib.logger import LoggerPlugin


@pytest.fixture
def iopipe_with_logger():
    plugin = LoggerPlugin("testlog", enabled=True)
    return IOpipeCore(
        token="test-suite", url="https://metrics-api.iopipe.com", plugins=[plugin]
    )


@pytest.fixture
def handler_with_logger(iopipe_with_logger):
    @iopipe_with_logger
    def _handler(event, context):
        context.iopipe.log.debug("I got nothing.")
        context.iopipe.log.info("I might have something.")
        context.iopipe.log.warn("Got something.")
        context.iopipe.log.error("And you have it, too.")
        context.iopipe.log.critical("And it's fatal.")

        try:
            raise ValueError("What do you value?")
        except Exception as e:
            context.iopipe.log.exception(e)

        print("This is not a misprint.")

    return iopipe_with_logger, _handler


@pytest.fixture
def iopipe_with_logger_disabled():
    plugin = LoggerPlugin(name="testlog", enabled=False)
    return IOpipeCore(
        token="test-suite", url="https://metrics-api.iopipe.com", plugins=[plugin]
    )


@pytest.fixture
def iopipe_with_logger_debug():
    plugin = LoggerPlugin(name="testlog", enabled=True)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def handler_with_logger_disabled(iopipe_with_logger_disabled):
    @iopipe_with_logger_disabled
    def _handler(event, context):
        pass

    return iopipe_with_logger_disabled, _handler


@pytest.fixture
def handler_with_logger_debug(iopipe_with_logger_debug):
    @iopipe_with_logger_debug
    def _handler(event, context):
        context.iopipe.log.debug("I should be logged.")

    return iopipe_with_logger_debug, _handler


@pytest.fixture
def iopipe_with_logger_use_tmp():
    plugin = LoggerPlugin(name="testlog", enabled=True, use_tmp=True)
    return IOpipeCore(
        token="test-suite", url="https://metrics-api.iopipe.com", plugins=[plugin]
    )


@pytest.fixture
def handler_with_logger_use_tmp(iopipe_with_logger_use_tmp):
    @iopipe_with_logger_use_tmp
    def _handler(event, context):
        context.iopipe.log.info("I should be logged to /tmp.")

    return iopipe_with_logger_use_tmp, _handler
