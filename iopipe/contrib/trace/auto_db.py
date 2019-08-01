import collections
import uuid

from .util import ensure_utf8

try:
    from redis import Redis
except ImportError:
    Redis = None

if Redis is not None:
    original_redis_execute_command = Redis.execute_command

Request = collections.namedtuple(
    "Request", ["command", "key", "hostname", "port", "connectionName", "db", "table"]
)


def collect_redis_metrics(trace, response):
    pass


def patch_redis_execute_command(context):
    if Redis is None:
        return

    if hasattr(Redis, "__monkey_patched"):
        return

    if not hasattr(context, "iopipe") or not hasattr(context.iopipe, "mark"):
        return

    def execute_command(self, *args, **kwargs):
        id = ensure_utf8(str(uuid.uuid4()))
        with context.iopipe.mark(id):
            response = original_redis_execute_command(self, *args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_redis_metrics(trace, response)
        return response

    Redis.execute_command = execute_command
    Redis.__monkey_patched = True


def restore_redis_execute_command():
    if Redis is not None:
        Redis.execute_command = original_redis_execute_command
        delattr(Redis, "__monkey_patched")


def patch_db_requests(context):
    patch_redis_execute_command(context)


def restore_db_requests():
    restore_redis_execute_command()
