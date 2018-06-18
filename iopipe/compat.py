import io
import sys

PY3 = sys.version_info[0] == 3

if PY3:
    string_types = (str,)
    StringIO = io.StringIO
else:
    string_types = (basestring,)  # noqa
    StringIO = io.BytesIO
