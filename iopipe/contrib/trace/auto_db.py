import collections
import uuid
import wrapt

from .util import ensure_utf8

Request = collections.namedtuple(
    "Request", ["command", "key", "hostname", "port", "connectionName", "db", "table"]
)


def collect_redis_metrics(context, trace, args, connection):
    command = key = None
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


def patch_redis_client(context):
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

    def pipeline_wrapper(wrapped, instance, args, kwargs):
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

    try:
        wrapt.wrap_function_wrapper(
            "redis.client", "Pipeline.immediate_execute_command", wrapper
        )
    except ModuleNotFoundError:  # pragma: no cover

        pass

    try:
        wrapt.wrap_function_wrapper(
            "redis.client", "Pipeline.execute", pipeline_wrapper
        )
    except ModuleNotFoundError:  # pragma: no cover

        pass


def restore_redis_client():
    """Restores the redis client"""
    try:
        from redis.client import Pipeline, Redis
    except ImportError:  # pragma: no cover
        pass
    else:
        if hasattr(Pipeline.execute, "__wrapped__"):
            setattr(Pipeline, "execute", Pipeline.execute.__wrapped__)
        if hasattr(Pipeline.immediate_execute_command, "__wrapped__"):
            setattr(
                Pipeline,
                "immediate_execute_command",
                Pipeline.immediate_execute_command.__wrapped__,
            )
        if hasattr(Redis.execute_command, "__wrapped__"):
            setattr(Redis, "execute_command", Redis.execute_command.__wrapped__)


def patch_db_requests(context):
    if not hasattr(context, "iopipe"):
        return

    patch_redis_client(context)


def restore_db_requests():
    restore_redis_client()
