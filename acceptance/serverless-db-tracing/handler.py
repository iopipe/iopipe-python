import os

import MySQLdb
import psycopg2

from iopipe import IOpipeCore
from iopipe.contrib.trace import TracePlugin

trace_plugin = TracePlugin(auto_db=True)
iopipe = IOpipeCore(debug=True, plugins=[trace_plugin])


@iopipe
def _mysqldb(event, context):
    conn = MySQLdb.connect(
        dbname=os.environ["DB_NAME"],
        host=os.environ["MYSQL_HOST"],
        passwd=os.environ["DB_PASSWORD"],
        port=os.environ["MYSQL_PORT"],
        username=os.environ["DB_USERNAME"],
    )
    cur = conn.cursor()

    cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abcdef"))

    cur.execute("SELECT * FROM test")
    cur.fetchone()

    cur.close()
    conn.close()


@iopipe
def _psycopg2(event, context):
    conn = psycopg2.connect(
        "postgres://%s:%s@%s:%s/%s"
        % (
            os.environ["DB_USERNAME"],
            os.environ["DB_PASSWORD"],
            os.environ["POSTGRES_HOST"],
            os.environ["POSTGRES_PORT"],
            os.environ["DB_NAME"],
        )
    )
    cur = conn.cursor()

    cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abcdef"))

    cur.execute("SELECT * FROM test")
    cur.fetchone()

    cur.close()
    conn.close()
