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

"""Unit tests for values.py."""

import pytest

from ansys.scade.pyhg.values import flatten


@pytest.mark.parametrize(
    'value, expected',
    [
        # scalar values
        ('7_ui8', [('', '7')]),
        ('3.14', [('', '3.14')]),
        ('+5_f32', [('', '+5')]),
        ("'x'", [('', "'x'")]),
        ('t', [('', 'True')]),
        ('true', [('', 'True')]),
        ('f', [('', 'False')]),
        ('false', [('', 'False')]),
        # vector
        (['9', '31_i32'], [('[0]', '9'), ('[1]', '31')]),
        # structure
        ({'r': '1.2_f64', 'i': '4.6'}, [('.r', '1.2'), ('.i', '4.6')]),
        # combination within a string
        (
            "(7_ui8, 3.14, +5_f32, {r : (t, f, true), i : 'x'})",
            [
                ('[0]', '7'),
                ('[1]', '3.14'),
                ('[2]', '+5'),
                ('[3].r[0]', 'True'),
                ('[3].r[1]', 'False'),
                ('[3].r[2]', 'True'),
                ('[3].i', "'x'"),
            ],
        ),
    ],
)
def test_flatten_nominal(value: str | list | dict, expected: list[tuple[str, str]]):
    literals = flatten(value)
    assert literals == expected
