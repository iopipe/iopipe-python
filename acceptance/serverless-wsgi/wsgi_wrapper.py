from iopipe import IOpipe
from wsgi import handler

iopipe = IOpipe()
handler = iopipe(handler)
