import collections
import uuid
import wrapt

from .util import ensure_utf8

Request = collections.namedtuple(
    "Request", ["command", "key", "hostname", "port", "connectionName", "db", "table"]
)


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

    try:
        wrapt.wrap_function_wrapper("pymongo.collection", "Collection.find", wrapper)
    except ModuleNotFoundError:  # pragma: no cover
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
            wrapt.wrap_function_wrapper(
                "pymongo.collection", "Collection.%s" % class_method, wrapper
            )


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

    try:
        wrapt.wrap_function_wrapper("redis.client", "Redis.execute_command", wrapper)
    except ModuleNotFoundError:  # pragma: no cover
        pass
    else:
        for module_name, class_method in [
            ("redis.client", "Pipeline.execute"),
            ("redis.client", "Pipeline.immediate_execute_command"),
        ]:
            wrapt.wrap_function_wrapper(module_name, class_method, pipeline_wrapper)


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

    patch_pymongo(context)
    patch_redis(context)


def restore_db_requests():
    restore_pymongo()
    restore_redis()
