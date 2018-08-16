from iopipe.compat import binary_types, string_types
from iopipe.contrib.trace.util import ensure_utf8


def test_ensure_utf8():
    assert isinstance(ensure_utf8(binary_types("foobar", "utf-8")), string_types)
