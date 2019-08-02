from redis import Redis

from iopipe.contrib.trace.auto_db import patch_db_requests, restore_db_requests


def test_patch_db_requests(mock_context_wrapper,):
    assert not hasattr(Redis.execute_command, "__wrapped__")

    patch_db_requests(mock_context_wrapper)

    assert hasattr(Redis.execute_command, "__wrapped__")

    restore_db_requests()

    assert not hasattr(Redis.execute_command, "__wrapped__")
