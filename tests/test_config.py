import os

from iopipe.config import set_config


def test_set_config__iopipe_enabled__default():
    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__title_case_true(monkeypatch):
    def mock_getenv(key, default=None):
        if key == 'IOPIPE_ENABLED':
            return 'True'
        return os.environ.get(key, default)

    monkeypatch.setattr(os, 'getenv', mock_getenv)
    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__small_caps_true(monkeypatch):
    def mock_getenv(key, default=None):
        if key == 'IOPIPE_ENABLED':
            return 'true'
        return os.environ.get(key, default)

    monkeypatch.setattr(os, 'getenv', mock_getenv)
    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__title_case_false(monkeypatch):
    def mock_getenv(key, default=None):
        if key == 'IOPIPE_ENABLED':
            return 'False'
        return os.environ.get(key, default)

    monkeypatch.setattr(os, 'getenv', mock_getenv)
    config = set_config()
    assert config['enabled'] is False


def test_set_config__iopipe_enabled__small_caps_false(monkeypatch):
    def mock_getenv(key, default=None):
        if key == 'IOPIPE_ENABLED':
            return 'false'
        return os.environ.get(key, default)

    monkeypatch.setattr(os, 'getenv', mock_getenv)
    config = set_config()
    assert config['enabled'] is False
