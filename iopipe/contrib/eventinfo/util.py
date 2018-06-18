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


def get_value(obj, path):
    if path.endswith(".length"):
        path = path.replace(".length", "|length(@)")
    parser = _get_parser(path)
    return parser.search(obj)


def has_key(obj, path):
    parser = _get_parser(path)
    result = parser.search(obj)
    return result is not None


def collect_all_keys(obj, initial_path, exclude_keys=None):
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
            if exclude_keys and ".".join(path[1:]) in exclude_keys:
                return
            out[".".join(path)] = o

    flatten(obj)
    return out


def slugify(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()
