import logging
import os
import time

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
    region = os.getenv("AWS_REGION", "")
    region = region if region and region in SUPPORTED_REGIONS else "us-west-2"
    return "signer.{region}.iopipe.com".format(region=region)


def get_signed_request(config, context, extension):
    """
    Returns a signed request URL from IOpipe

    :param config: The IOpipe config
    :param context: The AWS context to request a signed URL
    :param extension: The extension of the file to sign
    :returns: A signed request URL
    :rtype: str
    """
    url = "https://{hostname}/".format(hostname=get_signer_hostname())

    try:
        logger.debug("Requesting signed request URL from %s", url)
        response = requests.post(
            url,
            json={
                "arn": context.invoked_function_arn,
                "requestId": context.aws_request_id,
                "timestamp": int(time.time() * 1000),
                "extension": extension,
            },
            headers={"Authorization": config["token"]},
            timeout=config["network_timeout"],
        )
        response.raise_for_status()
    except Exception as e:
        logger.debug("Error requesting signed request URL: %s", e)
        if hasattr(e, "response"):
            logger.debug(e.response.content)
    else:
        response = response.json()
        logger.debug("Signed request URL received for %s", response["url"])
        return response
