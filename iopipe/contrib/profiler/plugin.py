from distutils.util import strtobool
import logging
import os
try:
    import cProfile as profile
except ImportError:
    import profile
import pstats
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

from iopipe.plugins import Plugin

from .request import get_signed_request, upload_profiler_report

logger = logging.getLogger(__name__)


class ProfilerPlugin(Plugin):
    name = 'profiler'
    version = '0.1.0'
    homepage = 'https://github.com/iopipe/iopipe-python'

    def __init__(self, enabled=False, sort='cumulative', restrictions=10):
        """
        Instantiates the profiler plugin

        :param enabled: Whether or not the profiler should be enabled for all invocations.
                        Alternatively this plugin can be enabled/disabled via the `IOPIPE_ENABLE_PROFILER` environment
                        variabl
        :type enabled: bool
        :param sort: The column(s) in which to sort the stats. One or more
                    columns can be set in the order in which they are to
                    be sorted. Keep in mind that each column has an
                    implicit sort order. Refer to pstats documentation for
                    more information.
        :type sort: str or list
        :param restrictions: Any restrictions to be applied to the stats.
                             Such as limiting results by count (int),
                             percentage (float) or by regular expression (str). One
                             or more restrictions can be applied via a list.
                             See pstats documentation for more information.
                    :type restrictions: int or float or str or list
        """
        self._enabled = enabled

        self.sort = sort
        if not isinstance(self.sort, (list, tuple)):
            self.sort = [self.sort]

        self.restrictions = restrictions or []
        if not isinstance(self.restrictions, (list, tuple)):
            self.restrictions = [self.restrictions]

    @property
    def enabled(self):
        return self._enabled or strtobool(os.getenv('IOPIPE_ENABLE_PROFILER', 'false'))

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        pass

    def pre_invoke(self, event, context):
        self.profile = None

        if self.enabled:
            self.profile = profile.Profile()
            self.profile.enable()

    def post_invoke(self, event, context):
        if self.profile is not None:
            self.profile.disable()

    def pre_report(self, report):
        if self.profile is not None:
            self.stream = StringIO()
            self.stats = pstats.Stats(self.profile, stream=self.stream)
            self.stats.sort_stats(*self.sort)
            self.stats.print_stats(*self.restrictions)

            signed_request = get_signed_request(report)
            upload_profiler_report(signed_request['signedRequest'], self.stream)

            plugin = [p for p in report.report['plugins'] if p['name'] == self.name]
            if plugin:
                plugin[0]['uploads'] = [signed_request['url']]

    def post_report(self, report):
        pass
