# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Unit tests for thgrt.py."""

import math

import pytest

from ansys.scade.pyhg.lib.thgrt import Thgrt


class Root:
    """
    Emulates an operator under test.

    The output value is a counter.
    """

    def __init__(self, init=0.0):
        self.o = init

    def call_cycle(self):
        self.o += 1


class TestThgrt(Thgrt):
    """Cache the failures."""

    def __init__(self, *args):
        super().__init__(*args)
        self.failures = []

    def log_failure(self, *args):
        self.failures.append(args)


def test_rt_no_check():
    rt = TestThgrt(Root(), 'Root', 'Procedure')
    # nothing to test
    rt.cycle(10)
    assert not rt.failures


def test_rt_single_check():
    rt = TestThgrt(Root(), 'Root', 'Procedure')
    # 1 == 1
    rt.check('o', 1)
    rt.cycle(1)
    assert not rt.failures
    # 2 != 1 but the check is over
    rt.cycle(1)
    assert not rt.failures


def test_rt_finite_sustain():
    rt = TestThgrt(Root(), 'Root', 'Procedure')
    # absolute tolerance
    rt.check('o', 2, sustain=4, tolerance=1)
    rt.cycle(3)
    assert not rt.failures
    rt.cycle(1)
    assert len(rt.failures) == 1
    # sustain is over, no more checks: the number of failures does not change
    rt.cycle(5)
    assert len(rt.failures) == 1


def test_rt_infinite_sustain():
    rt = TestThgrt(Root(), 'Root', 'Procedure')
    # absolute tolerance
    rt.check('o', 2, sustain=-1, tolerance=1)
    rt.cycle(3)
    assert not rt.failures
    # as many failures as there are cycles
    rt.cycle(5)
    assert len(rt.failures) == 5
    rt.uncheck('o')
    # sustain is over, no more checks: the number of failures does not change
    rt.cycle(5)
    assert len(rt.failures) == 5
    # manually check the output
    rt.close()


@pytest.mark.parametrize(
    'check, tolerance, expected',
    [
        # absolute tolerance
        (2.1001, 0.1, False),
        (1.8999, 0.1, False),
        (2.0100, 0.1, True),
        (1.9100, 0.1, True),
        # relative tolerance
        (2.1001, -0.1, True),
        (1.8999, -0.1, True),
        (2.1001, -0.02, False),
        (1.8999, -0.02, False),
    ],
)
def test_rt_rel_tolerance(check: float, tolerance: float, expected: bool):
    rt = TestThgrt(Root(), 'Root', 'Procedure')
    rt.cycle(1)
    # relative tolerance 2%
    rt.check('o', check, sustain=-1, tolerance=tolerance)
    rt.cycle(1)
    assert (not rt.failures) == expected
    # manually check the output
    rt.close()


def test_rt_log_failure(capsys):
    # do not stub the logging of failures
    rt = Thgrt(Root(), 'Root', 'Procedure')
    # clear output
    capsys.readouterr()
    rt.check('o', 0)
    rt.cycle(1)
    # something must have been written on stdout
    out = capsys.readouterr().out
    assert 'test failed' in out


def test_rt_robustness(capsys):
    rt = Thgrt(Root(), 'Root', 'Procedure')
    # clear output
    capsys.readouterr()
    rt.uncheck('a')
    # something must have been written on stdout
    out = capsys.readouterr().out
    assert out


@pytest.mark.parametrize(
    'init, check, expected',
    [
        (0, math.nan, False),
        (3.14, math.inf, False),
        (-1, -math.inf, False),
        (math.nan, 0, False),
        (math.inf, 1, False),
        (-math.inf, -3.14, False),
        (math.nan, math.inf, False),
        (math.nan, math.nan, True),
        (math.nan, -math.inf, False),
        (math.inf, math.inf, True),
        (math.inf, math.nan, False),
        (math.inf, -math.inf, False),
        (-math.inf, math.inf, False),
        (-math.inf, math.nan, False),
        (-math.inf, -math.inf, True),
    ],
)
def test_rt_special_real(init: float, check: float, expected: bool):
    rt = TestThgrt(Root(init), 'Root', 'Procedure')
    rt.check('o', check, tolerance=0.001)
    rt.cycle(1)
    assert not rt.failures if expected else rt.failures
