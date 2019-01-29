from distutils.util import strtobool
import os

from iopipe.plugins import Plugin

from .auto_http import patch_requests, restore_requests
from .marker import Marker
from .timeline import Timeline
from .util import add_timeline_measures


class TracePlugin(Plugin):
    name = "trace"
    version = "1.1.1"
    homepage = "https://github.com/iopipe/iopipe-python#trace-plugin"
    enabled = True

    def __init__(self, auto_measure=True, auto_http=True, http_filter=None):
        """
        Instantiates the trace plugin

        :param auto_measure: Whether or not to automatically measure traces
        :type auto_measure: bool
        :param auto_http: Whether or not to automatically trace HTTP requests
        :type auto_http: bool
        :param http_filter: A callable to filter http requests
        :type http_filter: function
        """
        self.auto_measure = auto_measure
        self.auto_http = auto_http is True or strtobool(
            os.getenv("IOPIPE_TRACE_AUTO_HTTP_ENABLED", "false")
        )
        self.http_filter = http_filter

        self.timeline = Timeline()

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        pass

    def pre_invoke(self, event, context):
        self.timeline = Timeline()
        context.iopipe.register("mark", Marker(self.timeline, context))

        if self.auto_http is True:
            patch_requests(context, self.http_filter)

    def post_invoke(self, event, context):
        context.iopipe.unregister("mark")

        if self.auto_http is True:
            restore_requests()

    def pre_report(self, report):
        if self.auto_measure:
            add_timeline_measures(self.timeline)

        for entry in self.timeline.get_entries():
            report.performance_entries.append(entry._asdict())

    def post_report(self, report):
        pass
