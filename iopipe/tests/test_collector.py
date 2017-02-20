import os
from iopipe.collector import get_collector_url


saved_region = os.environ.get('AWS_REGION')


def setup_function():
    # Clear AWS region between tests
    if os.environ.get('AWS_REGION') is not None:
        del os.environ['AWS_REGION']


def test_no_arguments():
    assert get_collector_url() == 'https://metrics-api.iopipe.com'


def test_with_regions():
    assert get_collector_url('ap-southeast-2') == ('https://'
                                                   'metrics-api'
                                                   '.ap-southeast-2'
                                                   '.iopipe.com')
    assert get_collector_url('eu-west-1') == ('https://'
                                              'metrics-api'
                                              '.eu-west-1'
                                              '.iopipe.com')
    assert get_collector_url('us-east-2') == ('https://'
                                              'metrics-api'
                                              '.us-east-2'
                                              '.iopipe.com')
    assert get_collector_url('us-west-1') == ('https://'
                                              'metrics-api'
                                              '.us-west-1'
                                              '.iopipe.com')
    assert get_collector_url('us-west-2') == ('https://'
                                              'metrics-api'
                                              '.us-west-2'
                                              '.iopipe.com')
    assert get_collector_url('us-east-1') == ('https://'
                                              'metrics-api'
                                              '.iopipe.com')


def test_with_unsupported_region():
    assert get_collector_url('eu-west-2') == 'https://metrics-api.iopipe.com'


def test_with_AWS_REGION():
    os.environ['AWS_REGION'] = 'eu-west-1'
    assert get_collector_url(os.getenv('AWS_REGION')) == ('https://'
                                                          'metrics-api'
                                                          '.eu-west-1'
                                                          '.iopipe.com')

    os.environ['AWS_REGION'] = 'us-west-1'
    assert get_collector_url(os.getenv('AWS_REGION')) == ('https://'
                                                          'metrics-api'
                                                          '.us-west-1'
                                                          '.iopipe.com')


# Restore AWS region
if saved_region is not None:
    os.environ['AWS_REGION'] = saved_region
