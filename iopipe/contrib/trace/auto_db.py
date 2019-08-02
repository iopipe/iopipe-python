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
        hostname=ensure_utf8(connection.host),
        port=ensure_utf8(connection.port),
        connectionName=None,
        db=ensure_utf8(connection.db),
        table=None,
    )
    request = request._asdict()
    context.iopipe.mark.db_trace(trace, request)


def patch_redis_execute_command(context):
    """
    Monkey patches redis client, if available. Overloads the
    execute_Command method to add tracing and metrics collection.
    """

    if not hasattr(context, "iopipe"):
        return

    def wrapper(wrapped, instance, args, kwargs):
        if not hasattr(context, "iopipe") or not hasattr(context.iopipe, "mark"):
            return wrapped(*args, **kwargs)

        pool = instance.connection_pool
        command_name = args[0]
        connection = instance.connection or pool.get_connection(command_name, **kwargs)

        id = ensure_utf8(str(uuid.uuid4()))
        with context.iopipe.mark(id):
            response = wrapped(*args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_redis_metrics(context, trace, args, connection)
        return response

    try:
        wrapt.wrap_function_wrapper("redis.client", "Redis.execute_command", wrapper)
    except ModuleNotFoundError:
        pass


def restore_redis_execute_command():
    """Restroes the original redis client execute_Command method"""
    try:
        from redis.client import Redis
    except ImportError:
        pass
    else:
        if hasattr(Redis.execute_command, "__wrapped__"):
            setattr(Redis, "execute_command", Redis.execute_command.__wrapped__)


def patch_db_requests(context):
    patch_redis_execute_command(context)


def restore_db_requests():
    restore_redis_execute_command()
