import wrapt

COMMAND_KEYWORDS = {
    "create": "table",
    "delete": "from",
    "insert": "into",
    "select": "from",
    "update": "update",
}


def parse_dsn(dsn):
    return dict(attr.split("=") for attr in dsn.split() if "=" in attr)


def table_name(query, command):
    if command in COMMAND_KEYWORDS:
        keyword = COMMAND_KEYWORDS[command]
        parts = query.lower().split()

        if keyword in parts:
            return parts[parts.index(keyword) + 1]


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

    def cursor(self, *args, **kwargs):  # pragma: no cover
        cursor = self.__wrapped__.cursor(*args, **kwargs)
        return CursorProxy(cursor, self)

    @property
    def extract_db(self):
        return self._self_kwargs.get("db", self._self_kwargs.get("database", ""))

    @property
    def extract_hostname(self):
        return self._self_kwargs.get("host", "localhost")

    @property
    def extract_port(self):
        return self._self_kwargs.get("port")


class AdapterProxy(wrapt.ObjectProxy):
    def prepare(self, *args, **kwargs):  # pragma: no cover
        if not args:
            return self.__wrapped__.prepare(*args, **kwargs)

        connection = args[0]

        if isinstance(connection, wrapt.ObjectProxy):
            connection = connection.__wrapped__

        return self.__wrapped__.prepare(connection, *args[1:], **kwargs)
