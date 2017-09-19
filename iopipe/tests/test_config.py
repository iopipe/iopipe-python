import os

from iopipe.config import is_enabled


def test_is_enabled_default():
    assert is_enabled() is True


def test_is_enabled_small_caps_true():
    os.environ['IOPIPE_ENABLED'] = 'true'
    assert is_enabled() is True


def test_is_enabled_title_case_true():
    os.environ['IOPIPE_ENABLED'] = 'True'
    assert is_enabled() is True


def test_is_enabled_small_caps_false():
    os.environ['IOPIPE_ENABLED'] = 'false'
    assert is_enabled() is False


def test_is_enabled_title_case_false():
    os.environ['IOPIPE_ENABLED'] = 'False'
    assert is_enabled() is False
