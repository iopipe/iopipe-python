import socket
import sys

import pytest

from iopipe import system


def test_read_bootid(benchmark):
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    benchmark(system.read_bootid)

    assert len(system.read_bootid()) > 0


def test_read_disk(benchmark):
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    disk = benchmark(system.read_disk)

    assert disk['totalMiB'] >= disk['usedMiB']
    assert round((disk['usedMiB'] / disk['totalMiB']) * 100, 2) == disk['usedPercentage']


def test_read_hostname(benchmark):
    benchmark(system.read_hostname)

    assert system.read_hostname() == socket.gethostname()


def test_read_meminfo(benchmark):
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    meminfo = benchmark(system.read_meminfo)

    assert 'MemFree' in meminfo
    assert 'MemTotal' in meminfo



def test_read_pid_stat(benchmark):
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    stat = benchmark(system.read_pid_stat, 'self')

    for key in ['utime', 'stime', 'cutime', 'cstime']:
        assert key in stat


def test_read_pid_status(benchmark):
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    status = benchmark(system.read_pid_status, 'self')

    for key in ['VmRSS', 'Threads', 'FDSize']:
        assert key in status


def test_read_stat(benchmark):
    if not sys.platform.startswith('linux'):
        pytest.skip('this test requires linux, skipping')

    cpus = benchmark(system.read_stat)

    for cpu in cpus:
        assert 'times' in cpu

        for key in ['idle', 'irq', 'sys', 'user', 'nice']:
            assert key in cpu['times']
