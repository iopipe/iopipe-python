import contextlib
import logging

try:
    import requests
except ImportError:
    from botocore.vendored import requests

logger = logging.getLogger(__name__)


def upload_profiler_report(url, data):
    """
    Uploads a profiler report to IOpipe

    :param url: The signed URL
    :param data: The profiler report
    """
    with contextlib.closing(data):
        data.file.seek(0)
        try:
            logger.debug('Uploading profiler report to IOpipe')
            response = requests.put(url, data=data.file)
            response.raise_for_status()
        except Exception as e:
            logger.debug('Error while uploading profiler report: %s', e)
            if hasattr(e, 'response'):
                logger.debug(e.response.content)
        else:
            logger.debug('Profiler report uploaded successfully')
