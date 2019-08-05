from redis.client import Pipeline, Redis

from iopipe.contrib.trace.auto_db import patch_db_requests, restore_db_requests


def test_patch_db_requests(mock_context_wrapper,):
    """Asserts that monkey patching occurs if iopipe present"""
    assert not hasattr(Redis.execute_command, "__wrapped__")
    assert not hasattr(Pipeline.execute, "__wrapped__")
    assert not hasattr(Pipeline.immediate_execute_command, "__wrapped__")

    patch_db_requests(mock_context_wrapper)

    assert hasattr(Redis.execute_command, "__wrapped__")
    assert hasattr(Pipeline.execute, "__wrapped__")
    assert hasattr(Pipeline.immediate_execute_command, "__wrapped__")

    restore_db_requests()

    assert not hasattr(Redis.execute_command, "__wrapped__")
    assert not hasattr(Pipeline.execute, "__wrapped__")
    assert not hasattr(Pipeline.immediate_execute_command, "__wrapped__")


def test_patch_db_requests_no_iopipe(mock_context,):
    """Asserts that monkey patching does not occur if IOpipe not present"""
    assert not hasattr(Redis.execute_command, "__wrapped__")
    assert not hasattr(Pipeline.execute, "__wrapped__")
    assert not hasattr(Pipeline.immediate_execute_command, "__wrapped__")

    delattr(mock_context, "iopipe")

    patch_db_requests(mock_context)

    assert not hasattr(Redis.execute_command, "__wrapped__")
    assert not hasattr(Pipeline.execute, "__wrapped__")
    assert not hasattr(Pipeline.immediate_execute_command, "__wrapped__")
