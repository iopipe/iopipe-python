from distutils.util import strtobool
import os

from .collector import get_collector_path, get_hostname


def set_config(**config):
    """
    Returns IOpipe configuration options, setting defaults as necessary.
    """
    config.setdefault('host', get_hostname())
    config.setdefault('path', get_collector_path())
    config.setdefault('client_id', os.getenv('IOPIPE_TOKEN') or os.getenv('IOPIPE_CLIENTID') or '')
    config.setdefault('debug', os.getenv('IOPIPE_DEBUG', False))
    config.setdefault('network_timeout', 5000)
    config.setdefault('timeout_window', os.getenv('IOPIPE_TIMEOUT_WINDOW', 150))
    config.setdefault('install_method', 'manual')
    config.setdefault('enabled', bool(strtobool(os.getenv('IOPIPE_ENABLED', 'true'))))
    config.setdefault('plugins', [])

    if 'url' in config:
        config['host'] = get_hostname(config['url'])
        config['path'] = get_collector_path(config['url'])

    if 'token' in config:
        config['client_id'] = config['token']

    try:
        config['debug'] = bool(config['debug'])
    except ValueError:
        config['debug'] = False

    try:
        config['network_timeout'] = int(config['network_timeout'])
    except ValueError:
        config['network_timeout'] = 5000

    try:
        config['timeout_window'] = int(config['timeout_window'])
    except ValueError:
        config['timeout_window'] = 150

    return config
