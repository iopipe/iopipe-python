import pytest

from iopipe.plugins import is_plugin, Plugin


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
            return 'incomplete-plugin'

        @property
        def version(self):
            return '0.1.0'

        @property
        def homepage(self):
            return 'https://github.com/iopipe'

    with pytest.raises(TypeError) as e:
        IncompletePlugin2()

    assert "Can't instantiate abstract class IncompletePlugin2" in str(e.value)

    class CompletePlugin(IncompletePlugin2):
        def setup(self, iopipe):
            pass

        def pre_invoke(self, event, context):
            pass

        def post_invoke(self, event, context):
            pass

        def pre_report(self, report):
            pass

        def post_report(self):
            pass

    plugin = CompletePlugin()

    assert is_plugin(plugin)
