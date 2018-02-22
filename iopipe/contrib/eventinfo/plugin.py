from iopipe.plugins import Plugin

from .event_types import log_for_event_type


class EventInfoPlugin(Plugin):
    name = 'event-info'
    version = '0.1.0'
    homepage = 'https://github.com/iopipe/iopipe-python#event-info-plugin'
    enabled = True

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        pass

    def pre_invoke(self, event, context):
        pass

    def post_invoke(self, event, context):
        log_for_event_type(event, context.iopipe.log)

    def pre_report(self, report):
        pass

    def post_report(self, report):
        pass
