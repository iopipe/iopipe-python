import collections
import uuid
import wrapt

from .dbapi import AdapterProxy, ConnectionProxy, CursorProxy, table_name
from .util import ensure_utf8

Request = collections.namedtuple(
    "Request", ["command", "key", "hostname", "port", "connectionName", "db", "table"]
)


def collect_mysql_metrics(context, trace, instance, args):
    connection = instance.connection_proxy

    db = connection.extract_db
    hostname = connection.extract_hostname
    port = connection.extract_port

    query = args[0]
    command = query.split()[0].lower()
    table = table_name(query, command)

    request = Request(
        command=ensure_utf8(command),
        key=None,
        hostname=ensure_utf8(hostname),
        port=ensure_utf8(port),
        connectionName=None,
        db=ensure_utf8(db),
        table=ensure_utf8(table),
    )
    request = request._asdict()
    context.iopipe.mark.db_trace(trace, "mysql", request)


def collect_psycopg2_metrics(context, trace, instance):
    try:
        from psycopg2.extensions import parse_dsn
    except ImportError:  # pragma: no cover
        from .dbapi import parse_dsn

    connection = instance.connection_proxy
    dsn = parse_dsn(connection.dsn)

    db = dsn.get("dbname")
    hostname = dsn.get("host", "localhost")
    port = dsn.get("port", 5432)

    query = instance.query
    command = query.split()[0].lower()
    table = table_name(query, command)

    request = Request(
        command=ensure_utf8(command),
        key=None,
        hostname=ensure_utf8(hostname),
        port=ensure_utf8(port),
        connectionName=None,
        db=ensure_utf8(db),
        table=ensure_utf8(table),
    )
    request = request._asdict()
    context.iopipe.mark.db_trace(trace, "postgresql", request)


def collect_pymongo_metrics(context, trace, instance, response):
    from pymongo.cursor import Cursor
    from pymongo.results import (
        BulkWriteResult,
        DeleteResult,
        InsertOneResult,
        InsertManyResult,
        UpdateResult,
    )

    command, key = None, None

    for command_name, key_attr, result_type in [
        ("bulk_write", "inserted_count", BulkWriteResult),
        ("delete", "deleted_count", DeleteResult),
        ("insert_one", "inserted_id", InsertOneResult),
        ("insert_many", "inserted_ids", InsertManyResult),
        ("update", ("upserted_id", "modified_count"), UpdateResult),
    ]:
        if isinstance(response, result_type):
            command = command_name
            if isinstance(key_attr, tuple):
                for attr in key_attr:
                    key = getattr(response, attr, None)
                    if key is not None:
                        break
            else:
                key = getattr(response, key_attr, None)
            if key is not None:
                key = str(key)
            break

    if isinstance(response, Cursor):  # pragman: no cover
        command = "find"
        key = response.retrieved

    hostname, port = None, None

    database = getattr(instance, "database", None)
    if database is not None:
        address = getattr(database, "address", None)
        if address is not None:
            hostname, port = address

    request = Request(
        command=ensure_utf8(command),
        key=ensure_utf8(key),
        hostname=ensure_utf8(hostname),
        port=ensure_utf8(port),
        connectionName=None,
        db=ensure_utf8(getattr(database, "name", None)),
        table=ensure_utf8(getattr(instance, "name", None)),
    )
    request = request._asdict()
    context.iopipe.mark.db_trace(trace, "mongodb", request)


def collect_redis_metrics(context, trace, args, connection):
    command, key = None, None
    if len(args) > 0:
        command = args[0]
    if len(args) > 1:
        key = args[1]

    request = Request(
        command=ensure_utf8(command),
        key=ensure_utf8(key),
        hostname=ensure_utf8(connection.get("host", "localhost")),
        port=ensure_utf8(connection.get("port", 6379)),
        connectionName=None,
        db=ensure_utf8(connection.get("db", 0)),
        table=None,
    )
    request = request._asdict()
    context.iopipe.mark.db_trace(trace, "redis", request)


def patch_mysqldb(context):
    """
    Monkey patches mysqldb client, if available. Overloads the
    execute method to add tracing and metrics collection.
    """

    class _CursorProxy(CursorProxy):
        def execute(self, *args, **kwargs):
            if not hasattr(context, "iopipe") or not hasattr(
                context.iopipe, "mark"
            ):  # pragma: no cover
                self.__wrapped__.execute(*args, **kwargs)
                return

            id = ensure_utf8(str(uuid.uuid4()))
            with context.iopipe.mark(id):
                self.__wrapped__.execute(*args, **kwargs)
            trace = context.iopipe.mark.measure(id)
            context.iopipe.mark.delete(id)
            collect_mysql_metrics(context, trace, self, args)

    class _ConnectionProxy(ConnectionProxy):
        def cursor(self, *args, **kwargs):
            cursor = self.__wrapped__.cursor(*args, **kwargs)
            return _CursorProxy(cursor, self)

    def connect_wrapper(wrapped, instance, args, kwargs):
        connection = wrapped(*args, **kwargs)
        return _ConnectionProxy(connection, args, kwargs)

    for module, attr, wrapper in [
        ("MySQLdb", "connect", connect_wrapper),
        ("MySQLdb", "Connection", connect_wrapper),
        ("MySQLdb", "Connect", connect_wrapper),
    ]:
        try:
            wrapt.wrap_function_wrapper(module, attr, wrapper)
        except Exception:  # pragma: no cover
            pass


def patch_psycopg2(context):
    """
    Monkey patches psycopg2 client, if available. Overloads the
    execute method to add tracing and metrics collection.
    """

    class _CursorProxy(CursorProxy):
        def execute(self, *args, **kwargs):
            if not hasattr(context, "iopipe") or not hasattr(
                context.iopipe, "mark"
            ):  # pragma: no cover
                self.__wrapped__.execute(*args, **kwargs)
                return

            id = ensure_utf8(str(uuid.uuid4()))
            with context.iopipe.mark(id):
                self.__wrapped__.execute(*args, **kwargs)
            trace = context.iopipe.mark.measure(id)
            context.iopipe.mark.delete(id)
            collect_psycopg2_metrics(context, trace, self)

    class _ConnectionProxy(ConnectionProxy):
        def cursor(self, *args, **kwargs):
            cursor = self.__wrapped__.cursor(*args, **kwargs)
            return _CursorProxy(cursor, self)

    def adapt_wrapper(wrapped, instance, args, kwargs):
        adapter = wrapped(*args, **kwargs)
        return AdapterProxy(adapter) if hasattr(adapter, "prepare") else adapter

    def connect_wrapper(wrapped, instance, args, kwargs):
        connection = wrapped(*args, **kwargs)
        return _ConnectionProxy(connection, args, kwargs)

    def register_type_wrapper(wrapped, instance, args, kwargs):
        def _extract_arguments(obj, scope=None):
            return obj, scope

        obj, scope = _extract_arguments(*args, **kwargs)

        if scope is not None:
            if isinstance(scope, wrapt.ObjectProxy):
                scope = scope.__wrapped__
            return wrapped(obj, scope)

        return wrapped(obj)

    for module, attr, wrapper in [
        ("psycopg2", "connect", connect_wrapper),
        ("psycopg2.extensions", "adapt", adapt_wrapper),
        ("psycopg2.extensions", "register_type", register_type_wrapper),
        ("psycopg2._psycopg", "register_type", register_type_wrapper),
        ("psycopg2._json", "register_type", register_type_wrapper),
    ]:
        try:
            wrapt.wrap_function_wrapper(module, attr, wrapper)
        except Exception:  # pragma: no cover
            pass


def patch_pymongo(context):
    """
    Monkey patches pymongo client, if available. Overloads the
    query methods to add tracing and metrics collection.
    """

    def wrapper(wrapped, instance, args, kwargs):
        if not hasattr(context, "iopipe") or not hasattr(
            context.iopipe, "mark"
        ):  # pragma: no cover
            return wrapped(*args, **kwargs)

        id = ensure_utf8(str(uuid.uuid4()))
        with context.iopipe.mark(id):
            response = wrapped(*args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_pymongo_metrics(context, trace, instance, response)
        return response

    for module, attr, _wrapper in [
        ("pymongo.collection", "Collection.find", wrapper),
        ("pymongo.collection", "Collection.bulk_write", wrapper),
        ("pymongo.collection", "Collection.delete_many", wrapper),
        ("pymongo.collection", "Collection.delete_one", wrapper),
        ("pymongo.collection", "Collection.insert_many", wrapper),
        ("pymongo.collection", "Collection.insert_one", wrapper),
        ("pymongo.collection", "Collection.replace_one", wrapper),
        ("pymongo.collection", "Collection.update_many", wrapper),
        ("pymongo.collection", "Collection.update_one", wrapper),
    ]:
        try:
            wrapt.wrap_function_wrapper(module, attr, _wrapper)
        except Exception:  # pragma: no cover
            pass


def patch_pymysql(context):
    """
    Monkey patches pymysql client, if available. Overloads the
    execute method to add tracing and metrics collection.
    """

    class _CursorProxy(CursorProxy):
        def execute(self, *args, **kwargs):
            if not hasattr(context, "iopipe") or not hasattr(
                context.iopipe, "mark"
            ):  # pragma: no cover
                self.__wrapped__.execute(*args, **kwargs)
                return

            id = ensure_utf8(str(uuid.uuid4()))
            with context.iopipe.mark(id):
                self.__wrapped__.execute(*args, **kwargs)
            trace = context.iopipe.mark.measure(id)
            context.iopipe.mark.delete(id)
            collect_mysql_metrics(context, trace, self, args)

    class _ConnectionProxy(ConnectionProxy):
        def cursor(self, *args, **kwargs):
            cursor = self.__wrapped__.cursor(*args, **kwargs)
            return _CursorProxy(cursor, self)

    def connect_wrapper(wrapped, instance, args, kwargs):
        connection = wrapped(*args, **kwargs)
        return _ConnectionProxy(connection, args, kwargs)

    try:
        wrapt.wrap_function_wrapper("pymysql", "connect", connect_wrapper)
    except Exception:  # pragma: no cover
        pass


def patch_redis(context):
    """
    Monkey patches redis client, if available. Overloads the
    execute methods to add tracing and metrics collection.
    """

    def wrapper(wrapped, instance, args, kwargs):
        if not hasattr(context, "iopipe") or not hasattr(
            context.iopipe, "mark"
        ):  # pragma: no cover
            return wrapped(*args, **kwargs)

        id = ensure_utf8(str(uuid.uuid4()))
        with context.iopipe.mark(id):
            response = wrapped(*args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_redis_metrics(
            context, trace, args, instance.connection_pool.connection_kwargs
        )
        return response

    def pipeline_wrapper(wrapped, instance, args, kwargs):  # pragma: no cover
        if not hasattr(context, "iopipe") or not hasattr(
            context.iopipe, "mark"
        ):  # pragma: no cover
            return wrapped(*args, **kwargs)

        # We don't need the entire command stack, just collect a stack count
        pipeline_args = ("PIPELINE", ensure_utf8(len(instance.command_stack)))

        id = ensure_utf8(str(uuid.uuid4()))
        with context.iopipe.mark(id):
            response = wrapped(*args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_redis_metrics(
            context, trace, pipeline_args, instance.connection_pool.connection_kwargs
        )
        return response

    for module, attr, _wrapper in [
        ("redis.client", "Redis.execute_command", wrapper),
        ("redis.client", "Pipeline.execute", wrapper),
        ("redis.client", "Pipeline.immediate_execute_command", wrapper),
    ]:
        try:
            wrapt.wrap_function_wrapper(module, attr, _wrapper)
        except Exception:  # pragma: no cover
            pass


def restore_mysqldb():
    """Restores mysqldb"""
    try:
        import MySQLdb
    except ImportError:  # pragma: no cover
        pass
    else:
        setattr(
            MySQLdb, "connect", getattr(MySQLdb.connect, "__wrapped__", MySQLdb.connect)
        )


def restore_psycopg2():
    """Restores psycopg2"""
    try:
        import psycopg2
    except ImportError:  # pragma: no cover
        pass
    else:
        setattr(
            psycopg2,
            "connect",
            getattr(psycopg2.connect, "__wrapped__", psycopg2.connect),
        )
        setattr(
            psycopg2.extensions,
            "register_type",
            getattr(
                psycopg2.extensions.register_type,
                "__wrapped__",
                psycopg2.extensions.register_type,
            ),
        )
        setattr(
            psycopg2._psycopg,
            "register_type",
            getattr(
                psycopg2._psycopg.register_type,
                "__wrapped__",
                psycopg2._psycopg.register_type,
            ),
        )
        setattr(
            psycopg2._json,
            "register_type",
            getattr(
                psycopg2._json.register_type,
                "__wrapped__",
                psycopg2._json.register_type,
            ),
        )


def restore_pymongo():
    """Restores pymongo"""
    try:
        from pymongo.collection import Collection
    except ImportError:  # pragma: no cover
        pass
    else:
        for class_method in (
            "bulk_write",
            "delete_many",
            "delete_one",
            "insert_many",
            "insert_one",
            "replace_one",
            "update_many",
            "update_one",
        ):
            if hasattr(getattr(Collection, class_method), "__wrapped__"):
                setattr(
                    Collection,
                    class_method,
                    getattr(Collection, class_method).__wrapped__,
                )


def restore_pymysql():
    """Restores pymysql"""
    try:
        import pymysql
    except ImportError:  # pragma: no cover
        pass
    else:
        setattr(
            pymysql, "connect", getattr(pymysql.connect, "__wrapped__", pymysql.connect)
        )


def restore_redis():
    """Restores the redis client"""
    try:
        from redis.client import Pipeline, Redis
    except ImportError:  # pragma: no cover
        pass
    else:
        if hasattr(Redis.execute_command, "__wrapped__"):
            setattr(Redis, "execute_command", Redis.execute_command.__wrapped__)
        for class_method in ["execute", "immediate_execute_command"]:
            if hasattr(getattr(Pipeline, class_method), "__wrapped__"):
                setattr(
                    Pipeline, class_method, getattr(Pipeline, class_method).__wrapped__
                )


def patch_db_requests(context):
    if not hasattr(context, "iopipe"):
        return

    patch_mysqldb(context)
    patch_psycopg2(context)
    patch_pymongo(context)
    patch_pymysql(context)
    patch_redis(context)


def restore_db_requests():
    restore_mysqldb()
    restore_psycopg2()
    restore_pymongo()
    restore_pymysql()
    restore_redis()
