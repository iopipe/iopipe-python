import abc


def get_plugin_meta(plugins):
    """
    Returns meta data about plugins.

    :param plugins: A list of plugins.
    :type plugins: list
    :returns: A list of dicts containing plugin meta data.
    :rtype: list
    """
    return [
        {
            "name": p.name,
            "version": p.version,
            "homepage": p.homepage,
            "enabled": p.enabled,
        }
        for p in plugins
        if is_plugin(p)
    ]


def is_plugin(plugin):
    """
    Returns true if the plugin implements the `Plugin` interface.

    :param plugin: The plugin to check.
    :returns: True if plugin, False otherwise.
    :rtype: bool
    """
    try:
        return isinstance(plugin, Plugin) or issubclass(plugin, Plugin)
    except TypeError:
        return False


def with_metaclass(meta, *bases):
    """Python 2 and 3 compatible way to do meta classes"""

    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, "temporary_class", (), {})


class Plugin(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractproperty
    def name(self):
        return NotImplemented

    @abc.abstractproperty
    def version(self):
        return NotImplemented

    @abc.abstractproperty
    def homepage(self):
        return NotImplemented

    @abc.abstractproperty
    def enabled(self):
        return NotImplemented

    @abc.abstractmethod
    def pre_setup(self, iopipe):
        return NotImplemented

    @abc.abstractmethod
    def post_setup(self, iopipe):
        return NotImplemented

    @abc.abstractmethod
    def pre_invoke(self, event, context):
        return NotImplemented

    @abc.abstractmethod
    def post_invoke(self, event, context):
        return NotImplemented

    @abc.abstractmethod
    def pre_report(self, report):
        return NotImplemented

    @abc.abstractmethod
    def post_report(self, report):
        return NotImplemented
