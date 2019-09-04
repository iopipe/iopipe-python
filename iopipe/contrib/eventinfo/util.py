import jmespath
import re

# Caches previously seen parsers
parsers = {}


def _format_path(path):
    return path.replace('["', '."').replace('.."', '."').replace('"]', '"')


def _get_parser(path):
    path = _format_path(path)
    parser = parsers.get(path)
    if parser is None:
        parser = jmespath.compile(path)
        parsers[path] = parser
    return parser


def get_value(obj, path, coerce_type=None):
    if path.endswith(".length"):
        path = path.replace(".length", "|length(@)")
    parser = _get_parser(path)
    value = parser.search(obj)
    if value is not None and callable(coerce_type):
        try:
            value = coerce_type(value)
        except (TypeError, ValueError):
            pass
    return value


def has_key(obj, path):
    parser = _get_parser(path)
    result = parser.search(obj)
    return result is not None


def collect_all_keys(obj, initial_path, exclude_keys=None, coerce_types=None):
    out = {}

    def flatten(o, path=None):
        if path is None:
            path = [initial_path]
        if isinstance(o, dict):
            for key in o:
                flatten(o[key], path + [key])
        elif isinstance(o, list):
            for i, value in enumerate(o):
                flatten(value, path + [str(i)])
        else:
            short_key = ".".join(path[1:])
            if exclude_keys and short_key in exclude_keys:
                return
            if (
                coerce_types
                and short_key in coerce_types
                and callable(coerce_types[short_key])
            ):
                try:
                    o = coerce_types[short_key](o)
                except (TypeError, ValueError):
                    pass
            out[".".join(path)] = o

    flatten(obj)
    return out


def slugify(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()
