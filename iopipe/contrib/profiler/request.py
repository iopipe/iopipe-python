import logging

try:
    import requests
except ImportError:
    from botocore.vendored import requests

from .signer import get_signer_hostname

logger = logging.getLogger(__name__)


def get_signed_request(report):
    """
    Returns a signed request URL from IOpipe

    :param report: The IOpipe report to request a signed URL
    :returns: A signed request URL
    :rtype: str
    """
    url = 'https://{hostname}/'.format(hostname=get_signer_hostname())

    try:
        logger.debug('Requesting signed request URL from %s' % url)
        response = requests.post(
            url,
            json={
                'arn': report.report['aws']['invokedFunctionArn'],
                'requestId': report.report['aws']['awsRequestId'],
                'timestamp': report.report['timestamp']
            },
            headers={
                'Authorization': report.report['client_id']
            })
        response.raise_for_status()
    except Exception as e:
        logger.debug('Error requesting signed request URL: %s' % e)
        if hasattr(e, 'response'):
            logger.debug(e.response.content)
    else:
        response = response.json()
        logger.debug('Signed request URL received for %s' % response['url'])
        return response


def upload_profiler_report(url, data):
    """
    Uploads a profiler report to IOpipe

    :param url: The signed URL
    :param data: The profiler report
    """
    data.seek(0)
    try:
        logger.debug('Uploading profiler report to IOpipe')
        response = requests.put(url, data=data)
        response.raise_for_status()
    except Exception as e:
        logger.debug('Error while uploading profiler report: %s' % e)
        if hasattr(e, 'response'):
            logger.debug(e.response.content)
    else:
        logger.debug('Profiler report uploaded successfully')
