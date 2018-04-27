import functools
import uuid

try:
    from requests.sessions import Session
except ImportError:
    Session = None

try:
    from botocore.vendored.requests.sessions import Session as BotocoreSession
except ImportError:
    BotocoreSession = None

from iopipe.compat import urlparse

if Session is not None:
    original_session_send = Session.send

if BotocoreSession is not None:
    original_botocore_session_send = BotocoreSession.send

EXCLUDE_HEADERS = ["Authorization", "Cookie", "Proxy-Authorization", "Set-Cookie"]

REQUEST_KEYS = [("method", "method"), ("url", "url")]

RESPONSE_KEYS = [("status_code", "statusCode")]

URLPARSE_KEYS = [
    ("fragment", "hash"),
    ("hostname", "hostname"),
    ("path", "path"),
    ("port", "port"),
    ("query", "query"),
    ("scheme", "protocol"),
]


def patch_session_send(context, auto_measure, http_filter):
    """
    Monkey patches requests' Session class, if available. Overloads the
    send method to add tracing and metrics collection.
    """
    if Session is None:
        return

    def send(self, *args, **kwargs):
        id = str(uuid.uuid4())
        with context.iopipe.mark(id):
            response = original_session_send(self, *args, **kwargs)
        if not auto_measure:
            context.iopipe.mark.measure(id)
        collect_metrics_for_response(response, context, id, http_filter)
        return response

    Session.send = send


def patch_botocore_session_send(context, auto_measure, http_filter):
    """
    Monkey patches botocore's vendored requests, if available. Overloads the
    Session class' send method to add tracing and metric collection.
    """
    if BotocoreSession is None:
        return

    def send(self, *args, **kwargs):
        id = str(uuid.uuid4())
        with context.iopipe.mark(id):
            response = original_botocore_session_send(self, *args, **kwargs)
        if not auto_measure:
            context.iopipe.mark.measure(id)
        collect_metrics_for_response(response, context, id, http_filter)
        return response

    BotocoreSession.send = send


def restore_session_send():
    """Restores the original Session send method"""
    if Session is not None:
        Session.send = original_session_send


def restore_botocore_session_send():
    """Restores the original botocore Session send method"""
    if BotocoreSession is not None:
        BotocoreSession.send = original_botocore_session_send


def patch_requests(context, auto_measure, http_filter):
    patch_session_send(context, auto_measure, http_filter)
    patch_botocore_session_send(context, auto_measure, http_filter)


def restore_requests():
    restore_session_send()
    restore_botocore_session_send()


def collect_metrics_for_response(response, context, id, http_filter):
    """
    Collects relevant metrics from a requests Response object and adds them to
    the IOpipe context.
    """
    if http_filter is not None and callable(http_filter):
        response = http_filter(response)
        if response is False:
            context.iopipe.mark.delete(id)
            return

    prefix = functools.partial("@iopipe/trace.{}.{}".format, id)
    context.iopipe.metric(prefix("type"), "autoHttp")

    for old_key, new_key in REQUEST_KEYS:
        if hasattr(response.request, old_key):
            context.iopipe.metric(
                prefix("request.%s" % new_key), getattr(response.request, old_key)
            )

    parsed_url = urlparse(response.request.url)
    for old_key, new_key in URLPARSE_KEYS:
        context.iopipe.metric(
            prefix("request.%s" % new_key), getattr(parsed_url, old_key)
        )

    for key, value in response.request.headers.items():
        if key not in EXCLUDE_HEADERS:
            context.iopipe.metric(prefix("request.headers.%s" % key), value)

    for old_key, new_key in RESPONSE_KEYS:
        if hasattr(response, old_key):
            context.iopipe.metric(
                prefix("response.%s" % new_key), getattr(response, old_key)
            )

    for key, value in response.headers.items():
        if key not in EXCLUDE_HEADERS:
            context.iopipe.metric(prefix("response.headers.%s" % key), value)
