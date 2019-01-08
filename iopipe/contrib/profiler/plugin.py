from concurrent.futures import Future, wait
from distutils.util import strtobool
import logging
import os

try:
    import cProfile as profile
except ImportError:
    import profile
import tempfile

from iopipe.plugins import Plugin
from iopipe.signer import get_signed_request

from .request import upload_profiler_report

logger = logging.getLogger(__name__)


class ProfilerPlugin(Plugin):
    name = "profiler"
    version = "1.0.0"
    homepage = "https://github.com/iopipe/iopipe-python#profiler-plugin"

    def __init__(self, enabled=False):
        """
        Instantiates the profiler plugin

        :param enabled: Whether or not the profiler should be enabled for all
                        invocations. Alternatively this plugin can be enabled/disabled
                        via the `IOPIPE_PROFILER_ENABLED` environment variable.
        :type enabled: bool
        """
        self._enabled = enabled

    @property
    def enabled(self):
        return self._enabled is True or bool(
            strtobool(os.getenv("IOPIPE_PROFILER_ENABLED", "false"))
        )

    def pre_setup(self, iopipe):
        self.iopipe = iopipe

    def post_setup(self, iopipe):
        pass

    def pre_invoke(self, event, context):
        self.context = context
        self.profile = None
        self.signed_request = None
        self.stats_file = None

        if self.enabled:
            self.signed_request = self.iopipe.submit_future(
                get_signed_request, self.iopipe.config, self.context, ".cprofile"
            )
            self.profile = profile.Profile()
            self.profile.enable()

    def post_invoke(self, event, context):
        if self.profile is not None:
            self.profile.disable()
            self.context.iopipe.label("@iopipe/plugin-profiler")

    def pre_report(self, report):
        if self.profile is not None:
            if self.signed_request is not None:
                if isinstance(self.signed_request, Future):
                    wait([self.signed_request])
                    self.signed_request = self.signed_request.result()
            if (
                self.signed_request is not None
                and "signedRequest" in self.signed_request
            ):
                with tempfile.NamedTemporaryFile(delete=False) as stats_file:
                    self.profile.dump_stats(stats_file.name)
                    self.iopipe.submit_future(
                        upload_profiler_report,
                        self.signed_request["signedRequest"],
                        stats_file.name,
                        self.iopipe.config,
                    )
                    self.stats_file = stats_file.name
                if "jwtAccess" in self.signed_request:
                    plugin = next((p for p in report.plugins if p["name"] == self.name))
                    if "uploads" not in plugin:
                        plugin["uploads"] = []
                    plugin["uploads"].append(self.signed_request["jwtAccess"])

    def post_report(self, report):
        pass
