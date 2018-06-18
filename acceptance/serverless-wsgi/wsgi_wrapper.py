import imp

from iopipe import IOpipe

wsgi = imp.load_source("wsgi", "wsgi.py")

iopipe = IOpipe()
handler = iopipe(wsgi.handler)
