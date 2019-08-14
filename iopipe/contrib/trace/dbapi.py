import wrapt


class CursorProxy(wrapt.ObjectProxy):
    def __init__(self, cursor, connection_proxy):
        super(CursorProxy, self).__init__(cursor)

        self._self_connection = connection_proxy

    @property
    def connection_proxy(self):
        return self._self_connection

    def execute(self, *args, **kwargs):
        self.__wrapped__.execute(*args, **kwargs)


class ConnectionProxy(wrapt.ObjectProxy):
    def __init__(self, connection, args, kwargs):
        super(ConnectionProxy, self).__init__(connection)

        self._self_args = args
        self._self_kwargs = kwargs

    def cursor(self, *args, **kwargs):
        cursor = self.__wrapped__.cursor(*args, **kwargs)
        return CursorProxy(cursor, self)

    @property
    def extract_hostname(self):
        return self._self_kwargs.get("host", "localhost")

    @property
    def extract_dbname(self):
        return self._self_kwargs.get("db", self._self_kwargs.get("database", ""))


class AdapterProxy(wrapt.ObjectProxy):
    def prepare(self, *args, **kwargs):
        if not args:
            return self.__wrapped__.prepare(*args, **kwargs)

        connection = args[0]

        if isinstance(connection, wrapt.ObjectProxy):
            connection = connection.__wrapped__

        return self.__wrapped__.prepare(connection, *args[1:], **kwargs)
