import warnings


class LogWrapper(object):
    def __init__(self, logger, context):
        self.logger = logger
        self.context = context

    def __call__(self, key, value):
        warnings.warn(
            "Calling context.iopipe.log() has been deprecated, use "
            "context.iopipe.metric() instead"
        )

    def __getattr__(self, name):
        self.context.iopipe.label("@iopipe/plugin-logger")
        return getattr(self.logger, name)
