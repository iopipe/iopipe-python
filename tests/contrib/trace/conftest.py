import MySQLdb
import psycopg2
import pymongo
import pymysql
import pytest
import redis
import requests

from iopipe import IOpipeCore
from iopipe.context import ContextWrapper
from iopipe.contrib.trace.marker import Marker
from iopipe.contrib.trace import TracePlugin
from iopipe.contrib.trace.timeline import Timeline


@pytest.fixture
def iopipe_with_trace():
    plugin = TracePlugin()
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def mock_context_wrapper(mock_context, iopipe_with_trace):
    return ContextWrapper(mock_context, iopipe_with_trace)


@pytest.fixture
def iopipe_with_trace_no_auto_measure():
    plugin = TracePlugin(auto_measure=False)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def iopipe_with_trace_auto_http():
    plugin = TracePlugin(auto_http=True)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def iopipe_with_trace_auto_http_filter():
    def http_filter(request, response):
        if request["url"].startswith("https://www.iopipe.com"):
            raise Exception("Do not trace this URL")

    plugin = TracePlugin(auto_http=True, http_filter=http_filter)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def handler_with_trace(iopipe_with_trace):
    @iopipe_with_trace
    def _handler(event, context):
        assert hasattr(context, "iopipe")
        assert hasattr(context.iopipe, "mark")
        assert hasattr(context.iopipe.mark, "start")
        assert hasattr(context.iopipe.mark, "end")
        assert hasattr(context.iopipe.mark, "measure")

        context.iopipe.mark.start("foo")
        context.iopipe.mark.end("foo")

    return iopipe_with_trace, _handler


@pytest.fixture
def handler_with_trace_no_auto_measure(iopipe_with_trace_no_auto_measure):
    @iopipe_with_trace_no_auto_measure
    def _handler(event, context):
        assert hasattr(context, "iopipe")
        assert hasattr(context.iopipe, "mark")
        assert hasattr(context.iopipe.mark, "start")
        assert hasattr(context.iopipe.mark, "end")
        assert hasattr(context.iopipe.mark, "measure")

        context.iopipe.mark.start("foo")
        context.iopipe.mark.end("foo")

    return iopipe_with_trace_no_auto_measure, _handler


@pytest.fixture
def handler_with_trace_auto_http(iopipe_with_trace_auto_http):
    @iopipe_with_trace_auto_http
    def _handler(event, context):
        requests.get("http://www.iopipe.com/")

    return iopipe_with_trace_auto_http, _handler


@pytest.fixture
def handler_with_trace_auto_https(iopipe_with_trace_auto_http):
    @iopipe_with_trace_auto_http
    def _handler(event, context):
        requests.get("https://www.iopipe.com/")

    return iopipe_with_trace_auto_http, _handler


@pytest.fixture
def handler_with_trace_auto_http_filter(iopipe_with_trace_auto_http_filter):
    @iopipe_with_trace_auto_http_filter
    def _handler(event, context):
        requests.get("https://www.iopipe.com/")

    return iopipe_with_trace_auto_http_filter, _handler


@pytest.fixture
def iopipe_with_trace_auto_http_filter_request():
    def http_filter(request, response):
        return None, response

    plugin = TracePlugin(auto_http=True, http_filter=http_filter)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def handler_with_trace_auto_http_filter_request(
    iopipe_with_trace_auto_http_filter_request
):
    @iopipe_with_trace_auto_http_filter_request
    def _handler(event, context):
        requests.get("https://www.iopipe.com/")

    return iopipe_with_trace_auto_http_filter_request, _handler


@pytest.fixture
def marker(timeline, mock_context):
    return Marker(timeline, mock_context)


@pytest.fixture
def timeline():
    return Timeline()


@pytest.fixture
def iopipe_with_trace_auto_db():
    plugin = TracePlugin(auto_db=True)
    return IOpipeCore(
        token="test-suite",
        url="https://metrics-api.iopipe.com",
        debug=True,
        plugins=[plugin],
    )


@pytest.fixture
def handler_with_trace_auto_db_redis(iopipe_with_trace_auto_db):
    @iopipe_with_trace_auto_db
    def _handler(event, context):
        r = redis.Redis(host="localhost", port=6379, db=0)
        r.set("foo", "bar")
        r.get("foo")

    return iopipe_with_trace_auto_db, _handler


@pytest.fixture
def handler_with_trace_auto_db_pymongo(iopipe_with_trace_auto_db):
    @iopipe_with_trace_auto_db
    def _handler(event, context):
        client = pymongo.MongoClient("localhost", 27017)
        db = client.test
        db.my_collection.insert_one({"x": 10})
        db.my_collection.find_one()
        db.my_collection.update_one({"x": 10}, {"$inc": {"x": 3}})

    return iopipe_with_trace_auto_db, _handler


@pytest.fixture
def handler_with_trace_auto_db_psycopg2(iopipe_with_trace_auto_db):
    @iopipe_with_trace_auto_db
    def _handler(event, context):
        conn = psycopg2.connect("postgres://username:password@localhost:5432/foobar")
        cur = conn.cursor()
        cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
        cur.execute("SELECT * FROM test")
        cur.fetchone()

    return iopipe_with_trace_auto_db, _handler


@pytest.fixture
def handler_with_trace_auto_db_mysqldb(iopipe_with_trace_auto_db):
    @iopipe_with_trace_auto_db
    def _handler(event, context):
        conn = MySQLdb.connect(
            db="foobar",
            host="localhost",
            port="3306",
            user="username",
            passwd="password",
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
        cur.execute("SELECT * FROM test")
        cur.fetchone()

    return iopipe_with_trace_auto_db, _handler


@pytest.fixture
def handler_with_trace_auto_db_pymysql(iopipe_with_trace_auto_db):
    @iopipe_with_trace_auto_db
    def _handler(event, context):
        conn = pymysql.connect(
            db="foobar",
            host="localhost",
            port="3306",
            user="username",
            passwd="password",
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
        cur.execute("SELECT * FROM test")
        cur.fetchone()

    return iopipe_with_trace_auto_db, _handler
