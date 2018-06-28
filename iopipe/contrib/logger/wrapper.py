class LogWrapper(object):
    def __init__(self, logger, context):
        self.logger = logger
        self.context = context

    def __call__(self, key, value):
        self.context.iopipe.metric(key, value)

    def __getattr__(self, name):
        self.context.iopipe.label("@iopipe/plugin-logger")
        return getattr(self.logger, name)
