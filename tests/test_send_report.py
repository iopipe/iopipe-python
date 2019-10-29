import mock

from iopipe.config import set_config
from iopipe.send_report import send_report


@mock.patch("os.environ", {})
@mock.patch("iopipe.send_report.session", autospec=True)
def test_send_report(mock_session):
    """Assert that a POST request is made when a report is sent"""
    send_report({"foo": "bar"}, set_config())

    mock_session.post.assert_called_once_with(
        "https://metrics-api.iopipe.com/v0/event",
        json={"foo": "bar"},
        headers=mock.ANY,
        timeout=5.0,
    )


@mock.patch("os.environ", {})
@mock.patch("iopipe.send_report.session", autospec=True)
def test_send_report_network_timeout(mock_session):
    """Assert that the timeout is changed when network_timeout is set"""
    send_report({"foo": "bar"}, set_config(network_timeout=60000))

    mock_session.post.assert_called_once_with(
        "https://metrics-api.iopipe.com/v0/event",
        json={"foo": "bar"},
        headers=mock.ANY,
        timeout=60,
    )
