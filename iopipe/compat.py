import io
import sys

PY3 = sys.version_info[0] == 3

if PY3:
    from urllib.parse import urlparse

    string_types = (str,)
    StringIO = io.StringIO
else:
    from urlparse import urlparse  # noqa

    string_types = (basestring,)  # noqa
    StringIO = io.BytesIO
