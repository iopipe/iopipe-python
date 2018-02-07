import os

from iopipe.collector import SUPPORTED_REGIONS


def get_signer_hostname():
    """
    Returns the IOpipe signer hostname for a region

    :returns: The signer hostname
    :rtype str
    """
    region = os.getenv('AWS_REGION', '')
    region = region if region and region in SUPPORTED_REGIONS else 'us-west-2'
    return 'signer.{region}.iopipe.com'.format(region=region)
