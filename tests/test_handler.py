import os

import pytest

from iopipe.handler import get_handler


def mock_handler(event, context):
    pass


def test_get_handler(monkeypatch):
    monkeypatch.setattr(
        os, "environ", {"IOPIPE_HANDLER": "tests.test_handler.mock_handler"}
    )
    func = get_handler()
    assert callable(func)


def test_get_handler_with_slashes(monkeypatch):
    monkeypatch.setattr(
        os, "environ", {"IOPIPE_HANDLER": "tests/test_handler.mock_handler"}
    )
    func = get_handler()
    assert callable(func)


def test_get_handler_improperly_formatted(monkeypatch):
    monkeypatch.setattr(os, "environ", {"IOPIPE_HANDLER": "foobar"})
    with pytest.raises(ValueError):
        func = get_handler()


def test_get_handler_non_existent_module(monkeypatch):
    monkeypatch.setattr(
        os, "environ", {"IOPIPE_HANDLER": "foo.bar.baz.is.not.a.module"}
    )
    with pytest.raises(ImportError):
        func = get_handler()
