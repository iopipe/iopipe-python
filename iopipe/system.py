import socket


def read_bootid():
    """
    Returns the system boot id.

    :returns: The system bood it.
    :rtype: str
    """
    with open('/proc/sys/kernel/random/boot_id') as bootid_file:
        return bootid_file.readline()


def read_hostname():
    """
    Returns the system hostname.

    :returns: The system hostname.
    :rtype: str
    """
    return socket.gethostname()


def read_meminfo():
    """
    Returns system memory usage information.

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
        'stime': int(stat[14]),
        'cutime': int(stat[15]),
        'cstime': int(stat[16]),
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
            line = row.split(':')
            status_value = line[1].rstrip('\t\n kB').lstrip()
            if line[0] in ['FDSize', 'Threads', 'VmRSS']:
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
                'times': {
                    'user': int(cpu_stat[1]),
                    'nice': int(cpu_stat[2]),
                    'sys': int(cpu_stat[3]),
                    'idle': int(cpu_stat[4]),
                    'irq': int(cpu_stat[6])
                }
            })
    return data
