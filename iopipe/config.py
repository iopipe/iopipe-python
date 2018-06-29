from distutils.util import strtobool
import os
import warnings

from .collector import get_collector_path, get_hostname


def set_config(**config):
    """
    Returns IOpipe configuration options, setting defaults as necessary.
    """
    config.setdefault("debug", bool(strtobool(os.getenv("IOPIPE_DEBUG", "false"))))
    config.setdefault("enabled", bool(strtobool(os.getenv("IOPIPE_ENABLED", "true"))))
    config.setdefault("host", get_hostname())
    config.setdefault("install_method", os.getenv("IOPIPE_INSTALL_METHOD", "manual"))
    config.setdefault("network_timeout", os.getenv("IOPIPE_NETWORK_TIMEOUT", 5000))
    config.setdefault("path", get_collector_path())
    config.setdefault("plugins", [])
    config.setdefault("sync_http", False)
    config.setdefault("timeout_window", os.getenv("IOPIPE_TIMEOUT_WINDOW", 500))
    config.setdefault(
        "token", os.getenv("IOPIPE_TOKEN") or os.getenv("IOPIPE_CLIENTID") or ""
    )

    if "client_id" in config:
        config["token"] = config.pop("client_id")

    if "url" in config:
        url = config.pop("url")

        config["host"] = get_hostname(url)
        config["path"] = get_collector_path(url)

    if "." in str(config["network_timeout"]):
        warnings.warn(
            "IOpipe's 'network_timeout' is now in milliseconds, expressed as an integer"
        )

    try:
        config["debug"] = bool(config["debug"])
    except ValueError:
        config["debug"] = False

    try:
        config["network_timeout"] = int(config["network_timeout"]) / 1000.0
    except ValueError:
        config["network_timeout"] = 5.0

    if "." in str(config["timeout_window"]):
        warnings.warn(
            "IOpipe's 'timeout_window' is now in milliseconds, expressed as an integer"
        )

    try:
        config["timeout_window"] = int(config["timeout_window"]) / 1000.0
    except ValueError:
        config["timeout_window"] = 0.5

    return config
