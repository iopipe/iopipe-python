from distutils.util import strtobool
import os

from .collector import get_collector_path, get_hostname


def set_config(**config):
    """
    Returns IOpipe configuration options, setting defaults as necessary.
    """
    config.setdefault('debug', bool(strtobool(os.getenv('IOPIPE_DEBUG', 'false'))))
    config.setdefault('enabled', bool(strtobool(os.getenv('IOPIPE_ENABLED', 'true'))))
    config.setdefault('host', get_hostname())
    config.setdefault('install_method', 'manual')
    config.setdefault('network_timeout', 5)
    config.setdefault('path', get_collector_path())
    config.setdefault('plugins', [])
    config.setdefault('timeout_window', os.getenv('IOPIPE_TIMEOUT_WINDOW', 0.5))
    config.setdefault('token', os.getenv('IOPIPE_TOKEN') or os.getenv('IOPIPE_CLIENTID') or '')

    if 'client_id' in config:
        config['token'] = config.pop('client_id')

    if 'url' in config:
        url = config.pop('url')

        config['host'] = get_hostname(url)
        config['path'] = get_collector_path(url)

    try:
        config['debug'] = bool(config['debug'])
    except ValueError:
        config['debug'] = False

    try:
        config['network_timeout'] = int(config['network_timeout'])
    except ValueError:
        config['network_timeout'] = 5

    try:
        config['timeout_window'] = float(config['timeout_window'])
    except ValueError:
        config['timeout_window'] = 1.5

    return config
