import platform
import socket
import sys

import pytest

from iopipe import system


def test_read_arch():
    assert system.read_arch() == platform.machine()


def test_read_bootid():
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    bootid = system.read_bootid()
    assert len(bootid) > 0


def test_read_hostname():
    hostname = system.read_hostname()
    assert hostname == socket.gethostname()


def test_read_meminfo():
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    meminfo = system.read_meminfo()
    assert 'MemFree' in meminfo
    assert 'MemTotal' in meminfo


def test_read_pid_stat():
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    stat = system.read_pid_stat('self')
    for key in ['utime', 'stime', 'cutime', 'cstime', 'rss']:
        assert key in stat


def test_read_pid_status():
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    status = system.read_pid_status('self')
    for key in ['VmRSS', 'Threads', 'FDSize']:
        assert key in status


def test_read_stat():
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    cpus = system.read_stat()
    for cpu in cpus:
        assert 'times' in cpu
        for key in ['idle', 'irq', 'sys', 'user', 'nice']:
            assert key in cpu['times']


def test_read_uptime():
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    uptime = system.read_uptime()
    assert uptime > 0
