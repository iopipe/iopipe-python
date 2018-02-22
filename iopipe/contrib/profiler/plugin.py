from distutils.util import strtobool
import logging
import os
try:
    import cProfile as profile
except ImportError:
    import profile
import tempfile

from iopipe.plugins import Plugin

from .request import get_signed_request, upload_profiler_report

logger = logging.getLogger(__name__)


class ProfilerPlugin(Plugin):
    name = 'profiler'
    version = '0.2.0'
    homepage = 'https://github.com/iopipe/iopipe-python#profiler-plugin'

    def __init__(self, enabled=False):
        """
        Instantiates the profiler plugin

        :param enabled: Whether or not the profiler should be enabled for all invocations.
                        Alternatively this plugin can be enabled/disabled via
                        the `IOPIPE_PROFILER_ENABLED` environment
                        variable.
        :type enabled: bool
        """
        self._enabled = enabled

    @property
    def enabled(self):
        return self._enabled is True or strtobool(os.getenv('IOPIPE_PROFILER_ENABLED', 'false'))

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
        pass

    def post_report(self, report):
        if self.profile is not None:
            with tempfile.NamedTemporaryFile() as stats_file:
                self.profile.dump_stats(stats_file.name)
                signed_request = get_signed_request(report)
                upload_profiler_report(signed_request['signedRequest'], stats_file.file)
