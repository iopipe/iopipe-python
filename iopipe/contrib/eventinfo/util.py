from .jsonpath import parser

# Caches previously seen parsers
PARSERS = {}


def get_value(obj, path):
    return_length = False
    if path.endswith('.length'):
        return_length = True
        path = path.replace('.length', '')

    parse = PARSERS.get(path)
    if parse is None:
        parse = parser.parse(path)
        PARSERS[path] = parse

    result = parse.find(obj)
    if return_length:
        return len(result)
    return result[0].value if result else None


def has_key(obj, path):
    parse = PARSERS.get(path)
    if parse is None:
        parse = parser.parse(path)
        PARSERS[path] = parse

    result = parse.find(obj)
    return len(result) > 0
