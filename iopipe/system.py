import platform
import socket


def read_arch():
    """
    Returns the system architecture.

    :returns: The system architecture.
    :rtype: str
    """
    return platform.machine()


def read_bootid():
    """
    REturns the system boot id.

    :returns: The system bood it.
    :rtype: str
    """
    with open('/proc/sys/kernel/random/boot_id') as bootid_file:
        return bootid_file.readline()


def read_hostname():
    """
    REturns the system hostname.

    :returns: The system hostname.
    :rtype: str
    """
    return socket.gethostname()


def read_meminfo():
    """
    REturns system memory usage information.

    :returns: The system memory usage.
    :rtype: dict
    """
    data = {}
    with open('/proc/meminfo') as meminfo_file:
        for row in meminfo_file:
            line = row.split(":")
            # Example content:
            # MemTotal:                3801016 kB
            # MemFree:                 1840972 kB
            # MemAvailable:        3287752 kB
            # HugePages_Total:             0
            data[line[0]] = int(line[1].lstrip().rstrip(" kB\n"))
    return data


def read_pid_stat(pid):
    """
    Returns system process stat information.

    :param pid: The process ID.
    :returns: The system stat information.
    :rtype: dict
    """
    with open('/proc/%s/stat' % (pid,)) as f:
        stat = f.readline().split(' ')
    return {
        'utime': int(stat[13]),
        'stime': int(stat[13]),
        'cutime': int(stat[15]),
        'cstime': int(stat[16]),
        'rss': int(stat[23])
    }


def read_pid_status(pid):
    """
    Returns the system process sstatus.

    :param pid: The process ID.
    :returns: The system process status.
    :rtype: dict
    """
    data = {}
    with open("/proc/%s/status" % (pid,)) as status_file:
        for row in status_file:
            line = row.split(":")
            status_value = line[1].rstrip("\t\n kB").lstrip()
            try:
                data[line[0]] = int(status_value)
            except ValueError:
                data[line[0]] = status_value
    return data


def read_stat():
    """
    Returns the system stat information.

    :returns: The system stat information.
    :rtype: list
    """
    data = []
    with open('/proc/stat') as stat_file:
        for line in stat_file:
            cpu_stat = line.split(' ')
            if cpu_stat[0][:3] != "cpu":
                break
            # First cpu line is aggregation of following lines, skip it
            if len(cpu_stat[0]) == 3:
                continue
            data.append({
                'name': cpu_stat[0],
                'times': {
                    'user': int(cpu_stat[1]),
                    'nice': int(cpu_stat[2]),
                    'sys': int(cpu_stat[3]),
                    'idle': int(cpu_stat[4]),
                    'irq': int(cpu_stat[6])
                }
            })
    return data


def read_uptime():
    """
    Returns the system uptime.

    :returns: The system uptime.
    :rtype: int
    """
    with open('/proc/uptime') as uptime_file:
        utf = uptime_file.readline().split(" ")
    return int(float(utf[0]))
