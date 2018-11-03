import collections
import copy
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
from .util import ensure_utf8

if Session is not None:
    original_session_send = Session.send

if BotocoreSession is not None:
    original_botocore_session_send = BotocoreSession.send

INCLUDE_HEADERS = [
    "accept",
    "accept-encoding",
    "age",
    "cache-control",
    "connection",
    "content-encoding",
    "content-length",
    "content-type",
    "date",
    "etag",
    "host",
    "server",
    "strict-transport-security",
    "user-agent",
    "vary",
]

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
        id = ensure_utf8(str(uuid.uuid4()))
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
    http_response = copy.deepcopy(http_response)
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
                {"key": ensure_utf8(k), "string": ensure_utf8(v)}
                for k, v in http_response.request.headers.items()
                if k.lower() in INCLUDE_HEADERS
            ]

        request = Request(
            hash=ensure_utf8(getattr(parsed_url, "fragment", None)),
            headers=request_headers,
            hostname=ensure_utf8(getattr(parsed_url, "hostname", None)),
            method=ensure_utf8(getattr(http_response.request, "method", None)),
            path=ensure_utf8(getattr(parsed_url, "path", None)),
            # TODO: Determine if this is redundant
            pathname=ensure_utf8(getattr(parsed_url, "path", None)),
            port=ensure_utf8(getattr(parsed_url, "port", None)),
            protocol=ensure_utf8(getattr(parsed_url, "scheme", None)),
            query=ensure_utf8(getattr(parsed_url, "query", None)),
            url=ensure_utf8(getattr(http_response.request, "url", None)),
        )

    response_headers = []
    if hasattr(http_response, "headers"):
        response_headers = [
            {"key": ensure_utf8(k), "string": ensure_utf8(v)}
            for k, v in http_response.headers.items()
            if k.lower() in INCLUDE_HEADERS
        ]

    response = Response(
        headers=response_headers,
        statusCode=ensure_utf8(getattr(http_response, "status_code", None)),
        statusMessage=None,
    )

    context.iopipe.mark.http_trace(trace, request, response)
