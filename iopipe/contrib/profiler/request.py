import logging
import os

try:
    import requests
except ImportError:
    from botocore.vendored import requests

logger = logging.getLogger(__name__)


def upload_profiler_report(url, filename, config):
    """
    Uploads a profiler report to IOpipe

    :param url: The signed URL
    :param filename: The profiler report file
    :param config: The IOpipe config
    """
    try:
        logger.debug("Uploading profiler report to IOpipe")
        with open(filename, "rb") as data:
            response = requests.put(url, data=data, timeout=config["network_timeout"])
        response.raise_for_status()
    except Exception as e:
        logger.debug("Error while uploading profiler report: %s", e)
        if hasattr(e, "response"):
            logger.debug(e.response.content)
    else:
        logger.debug("Profiler report uploaded successfully")
    finally:
        if os.path.isfile(filename):
            os.remove(filename)
