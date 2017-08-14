import os

from iopipe.collector import get_collector_path, get_hostname


saved_region = os.getenv('AWS_REGION')


def setup_function():
    # Clear AWS region between tests
    if os.getenv('AWS_REGION') is not None:
        del os.environ['AWS_REGION']


def test_get_collector_path_no_arguments():
    assert get_collector_path() == '/v0/event'


def test_get_collector_path_with_base_url():
    assert get_collector_path('https://metric-api.iopipe.com/foo') == '/foo/v0/event'


def test_get_hostname_no_arguments():
    assert get_hostname() == 'metrics-api.iopipe.com'


def test_get_hostname_with_regions():
    os.environ['AWS_REGION'] = 'ap-southeast-2'
    assert get_hostname() == 'metrics-api.ap-southeast-2.iopipe.com'

    os.environ['AWS_REGION'] = 'eu-west-1'
    assert get_hostname() == 'metrics-api.eu-west-1.iopipe.com'

    os.environ['AWS_REGION'] = 'us-east-2'
    assert get_hostname() == 'metrics-api.us-east-2.iopipe.com'

    os.environ['AWS_REGION'] = 'us-west-1'
    assert get_hostname() == 'metrics-api.us-west-1.iopipe.com'

    os.environ['AWS_REGION'] = 'us-west-2'
    assert get_hostname() == 'metrics-api.us-west-2.iopipe.com'


def test_get_hostname_with_unsupported_region():
    os.environ['AWS_REGION'] = 'eu-west-2'
    assert get_hostname() == 'metrics-api.iopipe.com'


# Restore AWS region
if saved_region is not None:
    os.environ['AWS_REGION'] = saved_region
