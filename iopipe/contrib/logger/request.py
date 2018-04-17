import logging

try:
    import requests
except ImportError:
    from botocore.vendored import requests

logger = logging.getLogger(__name__)


def upload_log_data(url, data):
    """
    Uploads log data to IOpipe.

    :param url: The signed URL
    :param data: The log data
    """
    data.seek(0)
    try:
        logger.debug('Uploading log data to IOpipe')
        response = requests.put(url, data=data)
        response.raise_for_status()
    except Exception as e:
        logger.debug('Error while uploading log data: %s', e)
        if hasattr(e, 'response'):
            logger.debug(e.response.content)
    else:
        logger.debug('Log data uploaded successfully')
