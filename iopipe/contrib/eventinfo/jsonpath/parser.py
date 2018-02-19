# Copyright 2013- Kenneth Knowles
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals

import logging
import os
import sys

from . import jsonpath
from ..ply import yacc
from .lexer import JsonPathLexer

logger = logging.getLogger(__name__)


def parse(string):
    return JsonPathParser().parse(string)


class JsonPathParser(object):
    """
    An LALR-parser for JsonPath
    """

    tokens = JsonPathLexer.tokens

    def __init__(self, debug=False, lexer_class=None):
        if self.__doc__ is None:
            raise Exception(
                'Docstrings have been removed! By design of PLY, jsonpath requires docstrings. You must not use '
                'PYTHONOPTIMIZE=2 or python -OO.')

        self.debug = debug
        self.lexer_class = lexer_class or JsonPathLexer  # Crufty but works around statefulness in PLY

    def parse(self, string, lexer=None):
        lexer = lexer or self.lexer_class()
        return self.parse_token_stream(lexer.tokenize(string))

    def parse_token_stream(self, token_iterator, start_symbol='jsonpath'):

        # Since PLY has some crufty aspects and dumps files, we try to keep them local
        # However, we need to derive the name of the output Python file :-/
        output_directory = os.path.dirname(__file__)
        try:
            module_name = os.path.splitext(os.path.split(__file__)[1])[0]
        except:
            module_name = __name__

        parsing_table_module = '_'.join([module_name, start_symbol, 'parsetab'])

        # And we regenerate the parse table every time; it doesn't actually take that long!
        new_parser = yacc.yacc(
            module=self,
            debug=self.debug,
            tabmodule=parsing_table_module,
            outputdir=output_directory,
            write_tables=0,
            start=start_symbol,
            errorlog=logger)

        return new_parser.parse(lexer=IteratorToTokenStream(token_iterator))

    # ===================== PLY Parser specification =====================

    precedence = [
        ('left', ','),
        ('left', 'DOUBLEDOT'),
        ('left', '.'),
        ('left', '|'),
        ('left', '&'),
        ('left', 'WHERE'),
    ]

    def p_error(self, t):
        raise Exception('Parse error at %s:%s near token %s (%s)' % (t.lineno, t.col, t.value, t.type))

    def p_jsonpath_binop(self, p):
        """jsonpath : jsonpath '.' jsonpath
                    | jsonpath DOUBLEDOT jsonpath
                    | jsonpath WHERE jsonpath
                    | jsonpath '|' jsonpath
                    | jsonpath '&' jsonpath"""
        op = p[2]

        if op == '.':
            p[0] = jsonpath.Child(p[1], p[3])
        elif op == '..':
            p[0] = jsonpath.Descendants(p[1], p[3])
        elif op == 'where':
            p[0] = jsonpath.Where(p[1], p[3])
        elif op == '|':
            p[0] = jsonpath.Union(p[1], p[3])
        elif op == '&':
            p[0] = jsonpath.Intersect(p[1], p[3])

    def p_jsonpath_fields(self, p):
        "jsonpath : fields_or_any"
        p[0] = jsonpath.Fields(*p[1])

    def p_jsonpath_named_operator(self, p):
        "jsonpath : NAMED_OPERATOR"
        if p[1] == 'this':
            p[0] = jsonpath.This()
        elif p[1] == 'parent':
            p[0] = jsonpath.Parent()
        else:
            raise Exception('Unknown named operator `%s` at %s:%s' % (p[1], p.lineno(1), p.lexpos(1)))

    def p_jsonpath_root(self, p):
        "jsonpath : '$'"
        p[0] = jsonpath.Root()

    def p_jsonpath_idx(self, p):
        "jsonpath : '[' idx ']'"
        p[0] = p[2]

    def p_jsonpath_slice(self, p):
        "jsonpath : '[' slice ']'"
        p[0] = p[2]

    def p_jsonpath_fieldbrackets(self, p):
        "jsonpath : '[' fields ']'"
        p[0] = jsonpath.Fields(*p[2])

    def p_jsonpath_child_fieldbrackets(self, p):
        "jsonpath : jsonpath '[' fields ']'"
        p[0] = jsonpath.Child(p[1], jsonpath.Fields(*p[3]))

    def p_jsonpath_child_idxbrackets(self, p):
        "jsonpath : jsonpath '[' idx ']'"
        p[0] = jsonpath.Child(p[1], p[3])

    def p_jsonpath_child_slicebrackets(self, p):
        "jsonpath : jsonpath '[' slice ']'"
        p[0] = jsonpath.Child(p[1], p[3])

    def p_jsonpath_parens(self, p):
        "jsonpath : '(' jsonpath ')'"
        p[0] = p[2]

    # Because fields in brackets cannot be '*' - that is reserved for array indices
    def p_fields_or_any(self, p):
        """fields_or_any : fields
                         | '*'    """
        if p[1] == '*':
            p[0] = ['*']
        else:
            p[0] = p[1]

    def p_fields_id(self, p):
        "fields : ID"
        p[0] = [p[1]]

    def p_fields_comma(self, p):
        "fields : fields ',' fields"
        p[0] = p[1] + p[3]

    def p_idx(self, p):
        "idx : NUMBER"
        p[0] = jsonpath.Index(p[1])

    def p_slice_any(self, p):
        "slice : '*'"
        p[0] = jsonpath.Slice()

    def p_slice(self, p):  # Currently does not support `step`
        "slice : maybe_int ':' maybe_int"
        p[0] = jsonpath.Slice(start=p[1], end=p[3])

    def p_maybe_int(self, p):
        """maybe_int : NUMBER
                     | empty"""
        p[0] = p[1]

    def p_empty(self, p):
        'empty :'
        p[0] = None


class IteratorToTokenStream(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def token(self):
        try:
            return next(self.iterator)
        except StopIteration:
            return None


if __name__ == '__main__':
    logging.basicConfig()
    parser = JsonPathParser(debug=True)
    print(parser.parse(sys.stdin.read()))
