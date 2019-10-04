import functools
import os

from iopipe.signer import SUPPORTED_REGIONS
from iopipe.signer import get_signer_hostname


def test_get_signer_hostname(monkeypatch):
    def mock_getenv(region, key, default=None):
        if key == "AWS_REGION":
            return region
        return os.environ.get(key, default)

    for region1, region2 in SUPPORTED_REGIONS.items():
        monkeypatch.setattr(os, "getenv", functools.partial(mock_getenv, region1))
        assert get_signer_hostname() == "signer.%s.iopipe.com" % region2
