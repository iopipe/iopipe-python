import mock
import os
import tempfile

from iopipe.contrib.profiler.request import upload_profiler_report


@mock.patch("iopipe.contrib.profiler.request.requests", autospec=True)
def test__upload_profiler_report__deletes_file(mock_requests):
    """Asserts that upload_profiler_report deletes the file when done uploading"""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    upload_profiler_report("", temp_file.name, {"network_timeout": 5})

    assert not os.path.exists(temp_file.name)
