class StreamToLogger(object):
    def __init__(self, logger):
        self.logger = logger

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.info(line.rstrip())
