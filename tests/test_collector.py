import functools
import os

from iopipe.collector import get_collector_path, get_hostname


def test_get_collector_path_no_arguments():
    assert get_collector_path() == "/v0/event"


def test_get_collector_path_with_base_url():
    assert get_collector_path("https://metric-api.iopipe.com/foo") == "/foo/v0/event"


def test_get_hostname_no_arguments(monkeypatch):
    def mock_getenv(key, default=None):
        if key == "AWS_REGION":
            return None
        return os.environ.get(key, default)

    monkeypatch.setattr(os, "getenv", mock_getenv)
    assert get_hostname() == "metrics-api.iopipe.com"


def test_get_hostname_with_regions(monkeypatch):
    def mock_getenv(region, key, default=None):
        if key == "AWS_REGION":
            return region
        return os.environ.get(key, default)

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "ap-northeast-1"))
    assert get_hostname() == "metrics-api.ap-northeast-1.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "ap-northeast-2"))
    assert get_hostname() == "metrics-api.ap-northeast-2.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "ap-south-1"))
    assert get_hostname() == "metrics-api.ap-south-1.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "ap-southeast-1"))
    assert get_hostname() == "metrics-api.ap-southeast-1.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "ap-southeast-2"))
    assert get_hostname() == "metrics-api.ap-southeast-2.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "ca-central-1"))
    assert get_hostname() == "metrics-api.ca-central-1.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "eu-central-1"))
    assert get_hostname() == "metrics-api.eu-central-1.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "eu-west-1"))
    assert get_hostname() == "metrics-api.eu-west-1.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "eu-west-2"))
    assert get_hostname() == "metrics-api.eu-west-2.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "us-east-2"))
    assert get_hostname() == "metrics-api.us-east-2.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "us-west-1"))
    assert get_hostname() == "metrics-api.us-west-1.iopipe.com"

    monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, "us-west-2"))
    assert get_hostname() == "metrics-api.us-west-2.iopipe.com"


def test_get_hostname_with_unsupported_region(monkeypatch):
    def mock_getenv(key, default=None):
        if key == "AWS_REGION":
            return "eu-west-3"
        return os.environ.get(key, default)

    monkeypatch.setattr(os, "getenv", mock_getenv)
    assert get_hostname() == "metrics-api.iopipe.com"
