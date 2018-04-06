import logging
import os

try:
    import requests
except ImportError:
    from botocore.vendored import requests

from .collector import SUPPORTED_REGIONS

logger = logging.getLogger(__name__)


def get_signer_hostname():
    """
    Returns the IOpipe signer hostname for a region

    :returns: The signer hostname
    :rtype str
    """
    region = os.getenv('AWS_REGION', '')
    region = region if region and region in SUPPORTED_REGIONS else 'us-west-2'
    return 'signer.{region}.iopipe.com'.format(region=region)


def get_signed_request(report, extension):
    """
    Returns a signed request URL from IOpipe

    :param report: The IOpipe report to request a signed URL
    :param extension: The extension of the file to sign.
    :returns: A signed request URL
    :rtype: str
    """
    url = 'https://{hostname}/'.format(hostname=get_signer_hostname())

    try:
        logger.debug('Requesting signed request URL from %s', url)
        response = requests.post(
            url,
            json={
                'arn': report.report['aws']['invokedFunctionArn'],
                'requestId': report.report['aws']['awsRequestId'],
                'timestamp': report.report['timestamp'],
                'extension': extension
            },
            headers={
                'Authorization': report.report['client_id']
            })
        response.raise_for_status()
    except Exception as e:
        logger.debug('Error requesting signed request URL: %s', e)
        if hasattr(e, 'response'):
            logger.debug(e.response.content)
    else:
        response = response.json()
        logger.debug('Signed request URL received for %s', response['url'])
        return response
