import pytest

from iopipe.contrib.trace import TracePlugin
from iopipe.plugins import get_plugin_meta, is_plugin, Plugin


def test_plugins_incomplete_interface():
    """Assert that a TypeError is raised if a plugin doesn't implmement the interface"""

    class IncompletePlugin1(Plugin):
        pass

    with pytest.raises(TypeError) as e:
        IncompletePlugin1()

    assert "Can't instantiate abstract class IncompletePlugin1" in str(e.value)

    class IncompletePlugin2(IncompletePlugin1):
        @property
        def name(self):
            return "incomplete-plugin"

        @property
        def version(self):
            return "0.1.0"

        @property
        def homepage(self):
            return "https://github.com/iopipe"

        @property
        def enabled(self):
            return True

    with pytest.raises(TypeError) as e:
        IncompletePlugin2()

    assert "Can't instantiate abstract class IncompletePlugin2" in str(e.value)

    class CompletePlugin(IncompletePlugin2):
        def pre_setup(self, iopipe):
            pass

        def post_setup(self, iopipe):
            pass

        def pre_invoke(self, event, context):
            pass

        def post_invoke(self, event, context):
            pass

        def pre_report(self, report):
            pass

        def post_report(self, report):
            pass

    plugin = CompletePlugin()

    assert is_plugin(plugin)


def test_is_plugin():
    class NotAPlugin(object):
        def do_nothing(self):
            pass

    assert not is_plugin(NotAPlugin)
    assert not is_plugin(NotAPlugin())
    assert is_plugin(TracePlugin)
    assert is_plugin(TracePlugin())


def test_get_plugin_meta():
    assert get_plugin_meta([TracePlugin()]) == [
        {
            "name": "trace",
            "version": "1.1.0",
            "homepage": "https://github.com/iopipe/iopipe-python#trace-plugin",
            "enabled": True,
        }
    ]
