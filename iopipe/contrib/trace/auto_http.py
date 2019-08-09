import collections
import uuid
import wrapt

from iopipe.compat import string_types, urlparse
from .util import ensure_utf8

INCLUDE_HEADERS = [
    "content-length",
    "content-type",
    "host",
    "server",
    "user-agent",
    "x-amz-target",
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


def patch_requests_session_send(context, http_filter, http_headers):
    """
    Monkey patches requests' session class, if available. Overloads the
    send method to add tracing and metrics collection.
    """

    def wrapper(wrapped, instance, args, kwargs):
        if not hasattr(context, "iopipe") or not hasattr(context.iopipe, "mark"):
            return wrapped(*args, **kwargs)
        id = ensure_utf8(str(uuid.uuid4()))
        with context.iopipe.mark(id):
            response = wrapped(*args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_metrics_for_response(
            response.request, response, context, trace, http_filter, http_headers
        )
        return response

    try:
        wrapt.wrap_function_wrapper("requests.sessions", "Session.send", wrapper)
    except Exception:  # pragma: no cover
        pass


def patch_botocore_session_send(context, http_filter, http_headers):
    """
    Monkey patches botocore's session, if available. Overloads the
    session class' send method to add tracing and metric collection.
    """

    def wrapper(wrapped, instance, args, kwargs):
        if not hasattr(context, "iopipe") or not hasattr(context.iopipe, "mark"):
            return wrapped(*args, **kwargs)
        id = str(uuid.uuid4())
        with context.iopipe.mark(id):
            response = wrapped(*args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_metrics_for_response(
            args[0], response, context, trace, http_filter, http_headers
        )
        return response

    try:
        wrapt.wrap_function_wrapper(
            "botocore.httpsession", "URLLib3Session.send", wrapper
        )
    except Exception:  # pragma: no cover
        pass


def patch_botocore_vendored_session_send(context, http_filter, http_headers):
    """
    Monkey patches botocore's vendored requests, if available. Overloads the
    session class' send method to add tracing and metric collection.
    """

    def wrapper(wrapped, instance, args, kwargs):
        if not hasattr(context, "iopipe") or not hasattr(context.iopipe, "mark"):
            return wrapped(*args, **kwargs)
        id = str(uuid.uuid4())
        with context.iopipe.mark(id):
            response = wrapped(*args, **kwargs)
        trace = context.iopipe.mark.measure(id)
        context.iopipe.mark.delete(id)
        collect_metrics_for_response(
            response.request, response, context, trace, http_filter, http_headers
        )
        return response

    try:
        wrapt.wrap_function_wrapper(
            "botocore.vendored.requests.sessions", "Session.send", wrapper
        )
    except Exception:  # pragma: no cover
        pass


def restore_requests_session_send():
    """Restores the original requests session send method"""
    try:
        from requests.sessions import Session as RequestsSession
    except ImportError:  # pragma: no cover
        pass
    else:
        if hasattr(RequestsSession.send, "__wrapped__"):
            setattr(RequestsSession, "send", RequestsSession.send.__wrapped__)


def restore_botocore_session_send():
    """Restores the original botocore session send method"""
    try:
        from botocore.httpsession import URLLib3Session as BotocoreSession
    except ImportError:  # pragma: no cover
        pass
    else:
        if hasattr(BotocoreSession.send, "__wrapped__"):
            setattr(BotocoreSession, "send", BotocoreSession.send.__wrapped__)


def restore_botocore_vendored_session_send():
    """Restores the original botocore vendored session send method"""
    try:
        from botocore.vendored.requests.sessions import (
            Session as BotocoreVendoredSession,
        )
    except ImportError:  # pragma: no cover
        pass
    else:
        if hasattr(BotocoreVendoredSession.send, "__wrapped__"):
            setattr(
                BotocoreVendoredSession,
                "send",
                BotocoreVendoredSession.send.__wrapped__,
            )


def patch_http_requests(context, http_filter, http_headers):
    if not hasattr(context, "iopipe"):
        return

    patch_requests_session_send(context, http_filter, http_headers)
    patch_botocore_session_send(context, http_filter, http_headers)
    patch_botocore_vendored_session_send(context, http_filter, http_headers)


def restore_http_requests():
    restore_requests_session_send()
    restore_botocore_session_send()
    restore_botocore_vendored_session_send()


def collect_metrics_for_response(
    http_request, http_response, context, trace, http_filter, http_headers
):
    """
    Collects relevant metrics from a requests Response object and adds them to
    the IOpipe context.
    """
    include_headers = INCLUDE_HEADERS
    if isinstance(http_headers, (list, tuple)):
        include_headers = include_headers + [
            key.lower()
            for key in http_headers
            if isinstance(http_headers, string_types)
        ]

    request = None
    if http_request:
        parsed_url = None
        if hasattr(http_request, "url"):
            parsed_url = urlparse(http_request.url)

        request_headers = []
        if hasattr(http_request, "headers"):
            request_headers = [
                {"key": ensure_utf8(k), "string": ensure_utf8(v)}
                for k, v in http_request.headers.items()
                if k.lower() in include_headers
            ]

        request = Request(
            hash=ensure_utf8(getattr(parsed_url, "fragment", None)),
            headers=request_headers,
            hostname=ensure_utf8(getattr(parsed_url, "hostname", None)),
            method=ensure_utf8(getattr(http_request, "method", None)),
            path=ensure_utf8(getattr(parsed_url, "path", None)),
            # TODO: Determine if this is redundant
            pathname=ensure_utf8(getattr(parsed_url, "path", None)),
            port=ensure_utf8(getattr(parsed_url, "port", None)),
            protocol=ensure_utf8(getattr(parsed_url, "scheme", None)),
            query=ensure_utf8(getattr(parsed_url, "query", None)),
            url=ensure_utf8(getattr(http_request, "url", None)),
        )

        # TODO: Possibly remove the namedtuple in favor of just a dict
        request = request._asdict()

    response_headers = []
    if hasattr(http_response, "headers"):
        response_headers = [
            {"key": ensure_utf8(k), "string": ensure_utf8(v)}
            for k, v in http_response.headers.items()
            if k.lower() in include_headers
        ]

    response = Response(
        headers=response_headers,
        statusCode=ensure_utf8(getattr(http_response, "status_code", None)),
        statusMessage=None,
    )

    # TODO: Possibly remove the namedtuple in favor of just a dict
    response = response._asdict()

    if http_filter is not None and callable(http_filter):
        try:
            request, response = http_filter(request, response)
        except Exception:
            return

    context.iopipe.mark.http_trace(trace, request, response)
