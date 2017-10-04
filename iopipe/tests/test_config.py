import os

from iopipe.config import set_config


def test_set_config__iopipe_enabled__default():
    config = set_config()
    assert config['enabled'] is True


def test_set_config__iopipe_enabled__disabled():
    os.environ['IOPIPE_ENABLED'] = 'False'

    config = set_config()
    assert config['enabled'] is False


def test_set_config__iopipe_enabled__enabled():
    os.environ['IOPIPE_ENABLED'] = 'True'

    config = set_config()
    assert config['enabled'] is True
