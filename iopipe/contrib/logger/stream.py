import sys


class StreamToLogger(object):
    def __init__(self, logger):
        self.logger = logger

    def __getattr__(self, name):
        return getattr(sys.__stdout__, name)

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.info(line.rstrip())
        sys.__stdout__.write(buf)
