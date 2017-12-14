from iopipe.plugins import Plugin

from .marker import Marker
from .timeline import Timeline
from .util import add_timeline_measures


class TracePlugin(Plugin):
    def __init__(self, auto_measure=False):
        self.auto_measure = auto_measure
        self.timeline = Timeline(use_timestamp=True)

    @property
    def name(self):
        return 'trace'

    @property
    def version(self):
        return '0.1.0'

    @property
    def homepage(self):
        return 'https://github.com/iopipe/iopipe-python'

    def setup(self, iopipe):
        self.timeline.mark('start:iopipe')

    def pre_invoke(self, event, context):
        context.iopipe.register('mark', Marker(self.timeline))

    def post_invoke(self, event, context):
        context.iopipe.unregister('mark')

    def pre_reporT(self, report):
        self.timeline.mark('end:iopipe')
        if self.auto_measure:
            add_timeline_measures(self.timeline)
        report.report['performanceEntries'] = [e._todict() for e in self.timeline.get_entries()]

    def post_reporT(self):
        self.timeline = Timeline()
