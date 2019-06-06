import collections
import copy
import uuid

try:
    from requests.sessions import Session as RequestsSession
except ImportError:
    RequestsSession = None

try:
    from botocore.httpsession import URLLib3Session as BotocoreSession
except ImportError:
    BotocoreSession = None

try:
    from botocore.vendored.requests.sessions import Session as BotocoreVendoredSession
except ImportError:
    BotocoreVendoredSession = None

from iopipe.compat import urlparse
from .util import ensure_utf8

if RequestsSession is not None:
    original_requests_session_send = RequestsSession.send

if BotocoreSession is not None:
    original_botocore_session_send = BotocoreSession.send

if BotocoreVendoredSession is not None:
    original_botocore_vendored_session_send = BotocoreVendoredSession.send

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


def patch_requests_session_send(context, http_filter):
    """
    Monkey patches requests' session class, if available. Overloads the
    send method to add tracing and metrics collection.
    """
    if RequestsSession is None:
        return

    if hasattr(RequestsSession, "send") and hasattr(
        RequestsSession.send, "monkey_patched"
    ):
        return

    def send(self, *args, **kwargs):
        id = ensure_utf8(str(uuid.uuid4()))
        with context.iopipe.mark(id):
            response = original_requests_session_send(self, *args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_metrics_for_response(response, context, trace, http_filter)
        return response

    RequestsSession.send = send
    RequestsSession.send.monkey_patched = True


def patch_botocore_session_send(context, http_filter):
    """
    Monkey patches botocore's session, if available. Overloads the
    session class' send method to add tracing and metric collection.
    """
    if BotocoreSession is None:
        return

    if hasattr(BotocoreSession, "send") and hasattr(
        BotocoreSession.send, "monkey_patched"
    ):
        return

    def send(self, *args, **kwargs):
        id = str(uuid.uuid4())
        with context.iopipe.mark(id):
            response = original_botocore_session_send(self, *args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_metrics_for_response(
            response, context, trace, http_filter, http_request=args[0]
        )
        return response

    BotocoreSession.send = send
    BotocoreSession.send.monkey_patched = True


def patch_botocore_vendored_session_send(context, http_filter):
    """
    Monkey patches botocore's vendored requests, if available. Overloads the
    session class' send method to add tracing and metric collection.
    """
    if BotocoreVendoredSession is None:
        return

    if hasattr(BotocoreVendoredSession, "send") and hasattr(
        BotocoreVendoredSession.send, "monkey_patched"
    ):
        return

    def send(self, *args, **kwargs):
        id = str(uuid.uuid4())
        with context.iopipe.mark(id):
            response = original_botocore_vendored_session_send(self, *args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_metrics_for_response(response, context, trace, http_filter)
        return response

    BotocoreVendoredSession.send = send
    BotocoreVendoredSession.send.monkey_patched = True


def restore_requests_session_send():
    """Restores the original requests session send method"""
    if RequestsSession is not None:
        RequestsSession.send = original_requests_session_send


def restore_botocore_session_send():
    """Restores the original botocore session send method"""
    if BotocoreSession is not None:
        BotocoreSession.send = original_botocore_session_send


def restore_botocore_vendored_session_send():
    """Restores the original botocore vendored session send method"""
    if BotocoreVendoredSession is not None:
        BotocoreVendoredSession.send = original_botocore_vendored_session_send


def patch_requests(context, http_filter):
    patch_requests_session_send(context, http_filter)
    patch_botocore_session_send(context, http_filter)
    patch_botocore_vendored_session_send(context, http_filter)


def restore_requests():
    restore_requests_session_send()
    restore_botocore_session_send()
    restore_botocore_vendored_session_send()


def collect_metrics_for_response(
    http_response, context, trace, http_filter, http_request=None
):
    """
    Collects relevant metrics from a requests Response object and adds them to
    the IOpipe context.
    """
    # We make copies to let the user mutate these objects via http_filter
    http_response = copy.deepcopy(http_response)
    if http_request is not None:
        http_response.request = copy.deepcopy(http_request)

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
