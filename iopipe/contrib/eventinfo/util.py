import jmespath

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
    if path.endswith('.length'):
        path = path.replace('.length', '|length(@)')
    parser = _get_parser(path)
    return parser.search(obj)


def has_key(obj, path):
    parser = _get_parser(path)
    result = parser.search(obj)
    return result is not None


def collect_all_keys(obj):
    out = {}

    def flatten(o, path=''):
        if isinstance(o, dict):
            for key in o:
                flatten(o[key], path + key + '.')
        elif isinstance(o, list):
            for i, value in enumerate(o):
                flatten(value, path + str(i) + '.')
        else:
            out[path[:-1]] = o

    flatten(obj)
    return out
