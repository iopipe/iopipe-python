import os

from functools import partial

from iopipe.config import set_config


def mock_getenv(expected_key, expected_value, key, default=None):
    if key == expected_key:
        return expected_value
    return os.environ.get(key, default)


def test_set_config__iopipe_debug__default():
    config = set_config()
    assert config['debug'] is False


def test_set_config__iopipe_debug__title_case_true(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_DEBUG', 'True'))
    config = set_config()
    assert config['debug'] is True


def test_set_config__iopipe_debug__small_caps_true(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_DEBUG', 'true'))
    config = set_config()
    assert config['debug'] is True


def test_set_config__iopipe_debug__title_case_false(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_DEBUG', 'False'))
    config = set_config()
    assert config['debug'] is False


def test_set_config__iopipe_debug__small_caps_false(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_DEBUG', 'false'))
    config = set_config()
    assert config['debug'] is False


def test_set_config__iopipe_enabled__default():
    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__title_case_true(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_ENABLED', 'True'))
    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__small_caps_true(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_ENABLED', 'true'))
    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__title_case_false(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_ENABLED', 'False'))
    config = set_config()
    assert config['enabled'] is False


def test_set_config__iopipe_enabled__small_caps_false(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_ENABLED', 'false'))
    config = set_config()
    assert config['enabled'] is False


def test_set_config__iopipe_install_method(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_INSTALL_METHOD', 'auto'))
    config = set_config()
    assert config['install_method'] == 'auto'


def test_set_config__iopipe_network_timeout(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_NETWORK_TIMEOUT', '60000'))
    config = set_config()
    assert config['network_timeout'] == 60.0

    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_NETWORK_TIMEOUT', 'not a number'))
    config = set_config()
    assert config['network_timeout'] == 5


def test_set_config__iopipe_timeout_window(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_TIMEOUT_WINDOW', '5000'))
    config = set_config()
    assert config['timeout_window'] == 5.0

    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_TIMEOUT_WINDOW', 'not a number'))
    config = set_config()
    assert config['timeout_window'] == 0.5


def test_set_config__iopipe_token(monkeypatch):
    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_TOKEN', 'foobar'))
    config = set_config()
    assert config['token'] == 'foobar'

    monkeypatch.setattr(os, 'getenv', partial(mock_getenv, 'IOPIPE_CLIENTID', 'barbaz'))
    config = set_config()
    assert config['token'] == 'barbaz'
