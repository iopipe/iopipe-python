import pytest

from iopipe.plugins import is_plugin, Plugin


def test_plugins_incomplete_interface():
    class MyPlugin(Plugin):
        pass

    with pytest.raises(TypeError) as e:
        myplugin = Plugin()
        assert e.value == ''
