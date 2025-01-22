# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Parser for SCADE Test scenario values."""

from keyword import iskeyword
import re

from pyparsing import (
    Forward,
    Regex,
    Suppress,
    Word,
    alphanums,
    alphas,
    delimitedList,
)


class Value:
    """A literal value."""

    def __init__(self, value) -> None:
        """Initialize the value."""
        if value in {'true', 't', 'TRUE', 'True', 'T'}:
            value = 'True'
        elif value in {'false', 'f', 'FALSE', 'False', 'F'}:
            value = 'False'
        else:
            # the following regular expressions are not exact
            # but should be enough for this context
            value = re.sub(r'(.+)_u?i\d+', r'\1', value)
            value = re.sub(r'(.+)_f\d+', r'\1', value)
        self.value = value

    def flatten(self, suffix, literals):
        """Flatten the value."""
        literals.append((suffix, self.value))


class ListValues:
    """A list of values."""

    def __init__(self, values) -> None:
        """Initialize the values."""
        self.values = values

    def flatten(self, suffix, literals):
        """Flatten the values."""
        for i, value in enumerate(self.values):
            value.flatten('%s[%d]' % (suffix, i), literals)


class StructFields:
    """A structure of fields."""

    def __init__(self, fields) -> None:
        """Initialize the fields."""
        self.fields = {name: value for name, value in fields}

    def flatten(self, suffix, literals):
        """Flatten the fields."""
        for name, value in self.fields.items():
            name = name + '_' if iskeyword(name) else name
            value.flatten('%s.%s' % (suffix, name), literals)


LBRACE, RBRACE, LPAR, RPAR, COLON, COMMA = map(Suppress, '{}():,')
ident = Word(alphas + '_', alphanums + '_').setName('name')
literal = Regex(r'[^ \t\(\)\{\},:]+').setParseAction(lambda t: Value(t[0]))
value_defn = Forward()
field_defn = (ident('name') + COLON + value_defn('value')).setParseAction(
    lambda t: (t['name'], t['value'])
)
struct_defn = (LBRACE + delimitedList(field_defn, ',')('fields') + RBRACE).setParseAction(
    lambda t: StructFields(t['fields'])
)
array_defn = (LPAR + delimitedList(value_defn, ',')('values') + RPAR).setParseAction(
    lambda t: ListValues(t['values'])
)
value_defn << (struct_defn | array_defn | literal)


def flatten(literal: object):
    """Flatten the literal."""

    def parse(literal: object) -> object:
        """Parse the literal."""
        if isinstance(literal, list):
            return ListValues([parse(_) for _ in literal])
        elif isinstance(literal, dict):
            return StructFields([(name, parse(value)) for name, value in literal.items()])
        else:
            assert isinstance(literal, str)
            return value_defn.parseString(literal)[0]

    literals = []
    tree = parse(literal)
    tree.flatten('', literals)

    return literals
