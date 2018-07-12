from .agent import IOpipeCore

from .contrib.eventinfo import EventInfoPlugin
from .contrib.profiler import ProfilerPlugin
from .contrib.trace import TracePlugin


class IOpipe(IOpipeCore):
    """
    The default IOpipe agent, pre-loaded with all the bundled plugins.
    """

    def __init__(self, *args, **kwargs):
        configured_plugins = kwargs.pop("plugins", None)
        plugins = [EventInfoPlugin(), ProfilerPlugin(), TracePlugin()]
        if configured_plugins is not None and isinstance(plugins, list):
            plugins = plugins + configured_plugins
        kwargs["plugins"] = plugins

        super(IOpipe, self).__init__(*args, **kwargs)
