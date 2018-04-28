class LogWrapper(object):
    def __init__(self, logger, context):
        self.logger = logger
        self.context = context

    def __call__(self, key, value):
        self.context.iopipe.metric(key, value)

    def __getattr__(self, name):
        self.context.iopipe.label('logs')
        if name in ['warn', 'warning']:
            self.context.iopipe.label('logs-warning')
        if name in ['critical', 'error', 'exception']:
            self.context.iopipe.label('logs-error')
        return getattr(self.logger, name)
