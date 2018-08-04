import collections
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

Request = collections.namedtuple(
    "Request",
    [
        "hash",
        "headers",
        "hostname",
        "method",
        "path",
        "pathname",
        "port",
        "protocol",
        "query",
        "url",
    ],
)

Response = collections.namedtuple(
    "Response", ["headers", "statusCode", "statusMessage"]
)


def patch_session_send(context, http_filter):
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
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_metrics_for_response(response, context, trace, http_filter)
        return response

    Session.send = send


def patch_botocore_session_send(context, http_filter):
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
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_metrics_for_response(response, context, trace, http_filter)
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


def patch_requests(context, http_filter):
    patch_session_send(context, http_filter)
    patch_botocore_session_send(context, http_filter)


def restore_requests():
    restore_session_send()
    restore_botocore_session_send()


def collect_metrics_for_response(http_response, context, trace, http_filter):
    """
    Collects relevant metrics from a requests Response object and adds them to
    the IOpipe context.
    """
    if http_filter is not None and callable(http_filter):
        http_response = http_filter(http_response)
        if http_response is False:
            return

    request = None
    if hasattr(http_response, "request"):
        parsed_url = None
        if hasattr(http_response.request, "url"):
            parsed_url = urlparse(http_response.request.url)

        request_headers = []
        if hasattr(http_response.request, "headers"):
            request_headers = [
                {"key": k, "string": v}
                for k, v in http_response.request.headers.items()
                if k not in EXCLUDE_HEADERS
            ]

    request = Request(
        hash=getattr(parsed_url, "fragment"),
        headers=request_headers,
        hostname=getattr(parsed_url, "hostname"),
        method=getattr(http_response.request, "method"),
        path=getattr(parsed_url, "path"),
        pathname=None,
        port=getattr(parsed_url, "port"),
        protocol=getattr(parsed_url, "scheme"),
        query=getattr(parsed_url, "query"),
        url=getattr(http_response.request, "url"),
    )

    response_headers = []
    if hasattr(http_response, "headers"):
        response_headers = [
            {"key": k, "string": v}
            for k, v in http_response.headers.items()
            if k not in EXCLUDE_HEADERS
        ]

    response = Response(
        headers=response_headers,
        statusCode=getattr(http_response, "status_code"),
        statusMessage=None,
    )

    context.iopipe.http_trace(trace, request, response)
