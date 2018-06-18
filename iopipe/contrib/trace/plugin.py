from iopipe.plugins import Plugin

from .marker import Marker
from .timeline import Timeline
from .util import add_timeline_measures


class TracePlugin(Plugin):
    name = "trace"
    version = "1.1.0"
    homepage = "https://github.com/iopipe/iopipe-python#trace-plugin"
    enabled = True

    def __init__(self, auto_measure=True):
        self.auto_measure = auto_measure
        self.timeline = Timeline()

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        pass

    def pre_invoke(self, event, context):
        context.iopipe.register("mark", Marker(self.timeline, context))

    def post_invoke(self, event, context):
        context.iopipe.unregister("mark")

    def pre_report(self, report):
        if self.auto_measure:
            add_timeline_measures(self.timeline)
        report.report["performanceEntries"] = [
            e._asdict() for e in self.timeline.get_entries()
        ]

    def post_report(self, report):
        self.timeline = Timeline()
