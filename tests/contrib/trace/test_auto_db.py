import MySQLdb
import psycopg2
from pymongo.collection import Collection
import pymysql
from redis.client import Pipeline, Redis
import wrapt

from iopipe.contrib.trace.auto_db import patch_db_requests, restore_db_requests

pymongo_collection_class_methods = (
    "bulk_write",
    "delete_many",
    "delete_one",
    "insert_many",
    "insert_one",
    "replace_one",
    "update_many",
    "update_one",
)


def test_patch_db_requests(mock_context_wrapper,):
    """Asserts that monkey patching occurs if iopipe present"""
    assert not hasattr(MySQLdb.connect, "__wrapped__")
    assert not hasattr(pymysql.connect, "__wrapped__")

    assert not isinstance(psycopg2.connect, wrapt.ObjectProxy)

    assert not hasattr(Redis.execute_command, "__wrapped__")
    assert not hasattr(Pipeline.execute, "__wrapped__")
    assert not hasattr(Pipeline.immediate_execute_command, "__wrapped__")

    for class_method in pymongo_collection_class_methods:
        assert not hasattr(getattr(Collection, class_method), "__wrapped__")

    patch_db_requests(mock_context_wrapper)

    assert hasattr(MySQLdb.connect, "__wrapped__")
    assert hasattr(pymysql.connect, "__wrapped__")

    assert isinstance(psycopg2.connect, wrapt.ObjectProxy)

    assert hasattr(Redis.execute_command, "__wrapped__")
    assert hasattr(Pipeline.execute, "__wrapped__")
    assert hasattr(Pipeline.immediate_execute_command, "__wrapped__")

    for class_method in pymongo_collection_class_methods:
        assert hasattr(getattr(Collection, class_method), "__wrapped__")

    restore_db_requests()

    assert not hasattr(MySQLdb.connect, "__wrapped__")
    assert not hasattr(pymysql.connect, "__wrapped__")

    assert not isinstance(psycopg2.connect, wrapt.ObjectProxy)

    assert not hasattr(Redis.execute_command, "__wrapped__")
    assert not hasattr(Pipeline.execute, "__wrapped__")
    assert not hasattr(Pipeline.immediate_execute_command, "__wrapped__")

    for class_method in pymongo_collection_class_methods:
        assert not hasattr(getattr(Collection, class_method), "__wrapped__")


def test_patch_db_requests_no_iopipe(mock_context,):
    """Asserts that monkey patching does not occur if IOpipe not present"""
    assert not hasattr(MySQLdb.connect, "__wrapped__")
    assert not hasattr(pymysql.connect, "__wrapped__")

    assert not isinstance(psycopg2.connect, wrapt.ObjectProxy)

    assert not hasattr(Redis.execute_command, "__wrapped__")
    assert not hasattr(Pipeline.execute, "__wrapped__")
    assert not hasattr(Pipeline.immediate_execute_command, "__wrapped__")

    for class_method in pymongo_collection_class_methods:
        assert not hasattr(getattr(Collection, class_method), "__wrapped__")

    delattr(mock_context, "iopipe")

    patch_db_requests(mock_context)

    assert not hasattr(MySQLdb.connect, "__wrapped__")
    assert not hasattr(pymysql.connect, "__wrapped__")

    assert not isinstance(psycopg2.connect, wrapt.ObjectProxy)

    assert not hasattr(Redis.execute_command, "__wrapped__")
    assert not hasattr(Pipeline.execute, "__wrapped__")
    assert not hasattr(Pipeline.immediate_execute_command, "__wrapped__")

    for class_method in pymongo_collection_class_methods:
        assert not hasattr(getattr(Collection, class_method), "__wrapped__")
