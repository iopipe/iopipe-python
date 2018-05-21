import mock
import os
import tempfile

from iopipe.contrib.logger.request import upload_log_data


@mock.patch('iopipe.contrib.logger.request.requests', autospec=True)
def test__upload_log_data__deletes_file(mock_requests):
    """Asserts that upload_log_data deletes the file when done uploading"""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    upload_log_data('', temp_file.name)

    assert not os.path.exists(temp_file.name)
