from iopipe.plugins import Plugin

from .event_types import metrics_for_event_type


class EventInfoPlugin(Plugin):
    name = "event-info"
    version = "1.2.0"
    homepage = "https://github.com/iopipe/iopipe-python#event-info-plugin"
    enabled = True

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        pass

    def pre_invoke(self, event, context):
        pass

    def post_invoke(self, event, context):
        metrics_for_event_type(event, context)

    def pre_report(self, report):
        pass

    def post_report(self, report):
        pass
