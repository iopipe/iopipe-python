import logging
import os

try:
    import requests
except ImportError:
    from botocore.vendored import requests

from iopipe.compat import StringIO

logger = logging.getLogger(__name__)


def upload_log_data(url, stream_or_file, config):
    """
    Uploads log data to IOpipe.

    :param url: The signed URL
    :param stream_or_file: The log data stream or file
    :param config: The IOpipe config
    """
    try:
        logger.debug("Uploading log data to IOpipe")
        if isinstance(stream_or_file, StringIO):
            stream_or_file.seek(0)
            response = requests.put(
                url, data=stream_or_file, timeout=config["network_timeout"]
            )
        else:
            with open(stream_or_file, "rb") as data:
                response = requests.put(
                    url, data=data, timeout=config["network_timeout"]
                )
        response.raise_for_status()
    except Exception as e:
        logger.debug("Error while uploading log data: %s", e)
        logger.exception(e)
        if hasattr(e, "response") and hasattr(e.response, "content"):
            logger.debug(e.response.content)
    else:
        logger.debug("Log data uploaded successfully")
    finally:
        if isinstance(stream_or_file, str) and os.path.exists(stream_or_file):
            os.remove(stream_or_file)
