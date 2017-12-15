import random
import uuid

from .system import read_hostname  # noqa


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
        'MemTotal': random.randint(0, 999999999),
        'MemFree': random.randint(0, 999999999),
        'MemAvailable': random.randint(0, 999999999),
        'HugePages_Total': random.randint(0, 999999999),
    }


def read_pid_stat(pid):
    """
    Mocks read_pid_stat as this is a Linux-specific operation.
    """
    return {
        'utime': random.randint(0, 999999999),
        'stime': random.randint(0, 999999999),
        'cutime': random.randint(0, 999999999),
        'cstime': random.randint(0, 999999999),
    }


def read_pid_status(pid):
    """
    Mocks read_pid_status as this is a Linux-specific operation.
    """
    return {
        'FDSize': random.randint(0, 999999999),
        'Threads': random.randint(0, 99999),
        'VmRSS': random.randint(0, 999999999),
    }


def read_stat():
    """
    Mocks read_stat as this is a Linux-specific operation.
    """
    return [{
        'times': {
            'user': random.randint(0, 999999999),
            'nice': random.randint(0, 999999999),
            'sys': random.randint(0, 999999999),
            'idle': random.randint(0, 999999999),
            'irq': random.randint(0, 999999999),
        }
    }]


def read_uptime():
    """
    Mocks read_updtime as this is a Linux-specific operaiton.
    """
    return random.randint(0, 999999999)
