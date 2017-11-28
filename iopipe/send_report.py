import logging

try:
    import requests
except ImportError:
    from botocore.vendored import requests

logger = logging.getLogger(__name__)
session = requests.Session()


def send_report(report, config):
    """
    Sends the report to IOpipe's collector.

    :param report: The report to be sent.
    :param config: The IOpipe agent configuration.
    """
    url = 'https://{host}{path}'.format(**config)

    try:
        response = session.post(url, json=report)
        response.raise_for_status()
    except Exception as e:
        logger.error('Error sending report to IOpipe: %s' % e)
        logger.exception(e)
