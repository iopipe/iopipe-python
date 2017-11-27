try:
    import requests
except ImportError:
    from botocore.vendored import requests

session = requests.Session()


def send_report(report, config):
    url = 'https://{host}{path}'.format(**config)
    session.post(url, json=report)
