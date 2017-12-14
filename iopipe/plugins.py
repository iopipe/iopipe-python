import abc


def is_plugin(plugin):
    """
    REturns true if the plugin implements the `Plugin` interface.

    :param plugin: The plugin to check.
    :returns: True if plugin, False otherwise.
    :rtype: bool
    """
    try:
        issubclass(plugin, Plugin)
    except TypeError:
        return False
    else:
        return True


def with_metaclass(meta, *bases):
    """Python 2 and 3 compatible way to do meta classes"""
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


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

    @abc.abstractmethod
    def setup(self, iopipe):
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
    def post_report(self):
        return NotImplemented
