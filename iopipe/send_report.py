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
    headers = {"Authorization": "Bearer {}".format(config["token"])}
    url = "https://{host}{path}".format(**config)

    try:
        response = session.post(
            url, json=report, headers=headers, timeout=config["network_timeout"]
        )
        response.raise_for_status()
    except Exception as e:
        logger.debug("Error sending report to IOpipe: %s" % e)
    else:
        logger.debug("Report sent to IOpipe successfully")
