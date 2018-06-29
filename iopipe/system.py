from __future__ import division

import os
import socket

MB_FACTOR = float(1 << 20)


def read_bootid():
    """
    Returns the system boot id.

    :returns: The system bood it.
    :rtype: str
    """
    with open("/proc/sys/kernel/random/boot_id", "rb") as bootid_file:
        return bootid_file.readline().decode("ascii")


def read_disk():
    """
    Returns disk usage for /tmp

    :returns: Disk usage (total, used, percentage used)
    :rtype dict
    """
    s = os.statvfs("/tmp")
    return {
        # This should report as 500MB, if not may need to be hardcoded
        # https://aws.amazon.com/lambda/faqs/
        "totalMiB": (s.f_blocks * s.f_bsize) / MB_FACTOR,
        "usedMiB": ((s.f_blocks - s.f_bfree) * s.f_frsize) / MB_FACTOR,
        "usedPercentage": round(
            (((s.f_blocks - s.f_bfree) * s.f_frsize) / (s.f_blocks * s.f_bsize)) * 100,
            2,
        ),
    }


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
    with open("/proc/meminfo", "rb") as meminfo_file:
        for row in meminfo_file:
            fields = row.split()
            # Example content:
            # MemTotal:                3801016 kB
            # MemFree:                 1840972 kB
            # MemAvailable:        3287752 kB
            # HugePages_Total:             0
            data[fields[0].decode("ascii")[:-1]] = int(fields[1]) * 1024
    return data


def read_pid_stat(pid="self"):
    """
    Returns system process stat information.

    :param pid: The process ID.
    :returns: The system stat information.
    :rtype: dict
    """
    with open("/proc/%s/stat" % (pid,), "rb") as f:
        stat = f.readline().split()
    return {
        "utime": int(stat[13]),
        "stime": int(stat[14]),
        "cutime": int(stat[15]),
        "cstime": int(stat[16]),
    }


def read_pid_status(pid="self"):
    """
    Returns the system process sstatus.

    :param pid: The process ID.
    :returns: The system process status.
    :rtype: dict
    """
    data = {}
    with open("/proc/%s/status" % (pid,), "rb") as status_file:
        for row in status_file:
            fields = row.split()
            if fields and fields[0] in [b"VmRSS:", b"Threads:", b"FDSize:"]:
                try:
                    data[fields[0].decode("ascii")[:-1]] = int(fields[1])
                except ValueError:
                    data[fields[0].decode("ascii")[:-1]] = fields[1].decode("ascii")
    return data


def read_stat():
    """
    Returns the system stat information.

    :returns: The system stat information.
    :rtype: list
    """
    data = []
    with open("/proc/stat", "rb") as stat_file:
        for line in stat_file:
            cpu_stat = line.split()
            if cpu_stat[0][:3] != b"cpu":
                break
            # First cpu line is aggregation of following lines, skip it
            if len(cpu_stat[0]) == 3:
                continue
            data.append(
                {
                    "times": {
                        "user": int(cpu_stat[1]),
                        "nice": int(cpu_stat[2]),
                        "sys": int(cpu_stat[3]),
                        "idle": int(cpu_stat[4]),
                        "irq": int(cpu_stat[6]),
                    }
                }
            )
    return data
