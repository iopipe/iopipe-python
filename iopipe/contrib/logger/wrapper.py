class LogWrapper(object):
    def __init__(self, logger, context):
        self.logger = logger
        self.context = context

    def __call__(self, key, value):
        return self.context.metric(key, value)

    def __getattr__(self, name):
        return getattr(self.logger, name)
