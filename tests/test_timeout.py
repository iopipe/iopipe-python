import time

import pytest

from iopipe.timeout import SignalTimeout, ThreadTimeout, TimeoutError


def test_signal_timeout():
    with pytest.raises(TimeoutError):
        with SignalTimeout(0.1):
            time.sleep(0.2)


def test_signal_timeout_cancel():
    with SignalTimeout(0.2):
        time.sleep(0.1)


def test_thread_timeout():
    with pytest.raises(TimeoutError):
        with ThreadTimeout(0.1):
            time.sleep(0.2)


def test_thread_timeout_cancel():
    with ThreadTimeout(0.2):
        time.sleep(0.1)
