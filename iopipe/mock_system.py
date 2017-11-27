import uuid

from .system import read_arch, read_hostname  # noqa


def read_bootid():
    """
    Mocks read_bootid as this is a Linux-specific operation.
    """
    return uuid.uuid4().hex


def read_meminfo():
    """
    Mocks read_meminfo as this is a Linux-specific operation.
    """
    return {
        'MemTotal': 3801016,
        'MemFree': 1840972,
        'MemAvailable': 3287752,
        'HugePages_Total': 0,
    }


def read_pid_stat(pid):
    """
    Mocks read_pid_stat as this is a Linux-specific operation.
    """
    return {
        'utime': 0,
        'stime': 0,
        'cutime': 0,
        'cstime': 0,
        'rss': 0,
    }


def read_pid_status(pid):
    """
    Mocks read_pid_status as this is a Linux-specific operation.
    """
    return {}


def read_stat():
    """
    Mocks read_stat as this is a Linux-specific operation.
    """
    return []


def read_uptime():
    """
    Mocks read_updtime as this is a Linux-specific operaiton.
    """
    return 0
