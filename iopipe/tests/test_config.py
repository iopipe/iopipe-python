import os

from iopipe.config import set_config


def test_set_config__iopipe_enabled__default():
    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__title_case_true():
    os.environ['IOPIPE_ENABLED'] = 'True'

    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__small_caps_true():
    os.environ['IOPIPE_ENABLED'] = 'true'

    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__title_case_false():
    os.environ['IOPIPE_ENABLED'] = 'False'

    config = set_config()
    assert config['enabled'] is False


def test_set_config__iopipe_enabled__small_caps_false():
    os.environ['IOPIPE_ENABLED'] = 'false'

    config = set_config()
    assert config['enabled'] is False
