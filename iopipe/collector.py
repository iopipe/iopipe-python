import os

from posixpath import join as urljoin

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

SUPPORTED_REGIONS = [
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ca-central-1",
    "eu-central-1",
    "eu-west-1",
    "eu-west-2",
    "us-east-2",
    "us-west-1",
    "us-west-2",
]


def get_collector_path(base_url=None):
    """
    Returns the IOpipe collector's path. By default this is `/v0/event`.

    :param base_url: An optional base URL to use.
    :returns: The collector's path.
    :rtype: str
    """
    if not base_url:
        return "/v0/event"
    event_url = urlparse(base_url)
    event_path = urljoin(event_url.path, "v0/event")
    if not event_path.startswith("/"):
        event_path = "/%s" % event_path
    if event_url.query:
        event_path = "?".join([event_path, event_url.query])
    return event_path


def get_hostname(config_url=None):
    """
    Returns the IOpipe collector's hostname. If  the `AWS_REGION` environment
    variable is not set or unsupported then `us-east-1` will be used by
    default. In this case, `us-east-1` is `metrics-api.iopipe.com`.

    :param config_url: A optional config URL to use.
    :returns: The collector's hostname.
    :rtype: str
    """
    region_string = ""
    if config_url:
        return urlparse(config_url).hostname
    aws_region = os.getenv("AWS_REGION")
    if aws_region and aws_region in SUPPORTED_REGIONS:
        region_string = ".%s" % aws_region
    return "metrics-api%s.iopipe.com" % region_string
