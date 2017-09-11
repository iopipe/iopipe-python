def get_pid_stat(pid):
    with open('/proc/%s/stat' % (pid,)) as f:
        stat = f.readline().split(' ')
    return {
        'utime': int(stat[13]),
        'stime': int(stat[13]),
        'cutime': int(stat[15]),
        'cstime': int(stat[16]),
        'rss': int(stat[23])
    }
