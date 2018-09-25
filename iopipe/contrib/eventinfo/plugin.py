from distutils.util import strtobool
import os

from iopipe.plugins import Plugin

from .event_types import metrics_for_event_type


class EventInfoPlugin(Plugin):
    name = "event-info"
    version = "1.3.0"
    homepage = "https://github.com/iopipe/iopipe-python#event-info-plugin"

    def __init__(self, enabled=True):
        """
        Instantiates the event info plugin

        :param enabled: Whether or not event info should be enabled for all
                        invocations. Alternatively this plugin can be enabled/disabled
                        via the `IOPIPE_EVENT_INFO_ENABLED` environment variable.
        :type enabled: bool
        """
        self._enabled = enabled

    @property
    def enabled(self):
        return self._enabled is True or bool(
            strtobool(os.getenv("IOPIPE_EVENT_INFO_ENABLED", "false"))
        )

    def pre_setup(self, iopipe):
        pass

    def post_setup(self, iopipe):
        pass

    def pre_invoke(self, event, context):
        pass

    def post_invoke(self, event, context):
        if self.enabled:
            metrics_for_event_type(event, context)

    def pre_report(self, report):
        pass

    def post_report(self, report):
        pass
