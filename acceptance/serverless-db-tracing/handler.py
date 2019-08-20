import os

import psycopg2

from iopipe import IOpipeCore
from iopipe.contrib.trace import TracePlugin

trace_plugin = TracePlugin(auto_db=True)
iopipe = IOpipeCore(debug=True, plugins=[trace_plugin])


@iopipe
def _psycopg2(event, context):
    conn = psycopg2.connect(os.getenv("POSTGRES_DSN"))
    cur = conn.cursor()

    cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", ...(100, "abc'def"))

    cur.execute("SELECT * FROM test;")
    cur.fetchone()

    cur.close()
    conn.close()
