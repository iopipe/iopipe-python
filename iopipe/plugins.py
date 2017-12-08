import abc


def with_metaclass(meta, *bases):
    """Python 2 and 3 compatible way to do meta classes"""
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


class PluginRegistry(object):
    def __init__(self):
        self.registry = {}

    def register(self, plugin):
        self.registry[plugin.name] = plugin

    def keys(self):
        return self.registry.keys()

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def __getitem__(self, name):
        return self.registry[name]


registry = PluginRegistry()
del PluginRegistry


class Registerable(abc.ABCMeta):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(Registerable, cls).__new__(cls, clsname, bases, attrs)
        registry.register(newclass)
        return newclass


class Plugin(with_metaclass(Registerable, object)):
    def __init__(self):
        pass

    @abc.abstractproperty
    def name(self):
        return NotImplemented

    @abc.abstractproperty
    def version(self):
        return NotImplemented

    @abc.abstractmethod
    def pre_setup(self):
        return NotImplemented

    @abc.abstractmethod
    def post_setup(self):
        return NotImplemented

    @abc.abstractmethod
    def pre_invoke(self):
        return NotImplemented

    @abc.abstractmethod
    def post_invoke(self):
        return NotImplemented

    @abc.abstractmethod
    def pre_reporT(self):
        return NotImplemented

    @abc.abstractmethod
    def post_reporT(self):
        return NotImplemented
