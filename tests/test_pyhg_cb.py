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

"""Unit tests for pyhg.py."""

import io
from pathlib import Path
from typing import Optional

import pytest
from scade.code.suite.mapping import c
import scade.model.project.stdproject as std
import scade.model.testenv as qte

import ansys.scade.pyhg.pyhg as pyhg
from conftest import find_configuration, load_project


@pytest.fixture(scope='session')
def first_p1() -> tuple[std.Project, qte.Procedure, c.MappingFile]:
    """Load the project."""
    first_dir = Path(__file__).parent / 'First'
    path = first_dir / 'Model' / 'First.etp'
    project = load_project(path)
    path = first_dir / 'Test' / 'P1.stp'
    application = qte.TestApplication()
    application.load_procedure_tcl(str(path))
    procedure = application.procedures[0]
    kcg_target_dir = first_dir / 'Model' / 'KCG'
    mf = c.open_mapping(str(kcg_target_dir / 'mapping.xml'))
    return project, procedure, mf


class TestPyHG(pyhg.PyHG):
    """Redirects the printouts."""

    def __init__(self, mf: Optional[c.MappingFile] = None, path: str = ''):
        super().__init__()
        self.stream = io.StringIO()
        self.f = self.stream
        if mf:
            assert path
            operator = self.get_operator(mf, path)
            assert operator
            self.init_ios(mf, operator)

    def writeln(self, text: str):
        assert self.f
        self.f.write(text)
        self.f.write('\n')

    def read(self) -> str:
        self.stream.flush()
        text = self.stream.getvalue()
        # reset
        self.stream = io.StringIO()
        self.f = self.stream
        return text.strip('\n')


@pytest.mark.parametrize(
    'number, expected',
    [('', 'thgrt.cycle(1)'), ('9', 'thgrt.cycle(9)')],
)
def test_on_cycle(number: str, expected: str):
    cls = TestPyHG()
    pyhg.on_cycle(cls, 12, 46, number)
    text = cls.read()
    assert text == expected


@pytest.mark.parametrize(
    'text, expected',
    [('# hello', '# hello'), ('#', '')],
)
def test_on_comment(text: str, expected: str):
    cls = TestPyHG()
    pyhg.on_comment(cls, 12, 46, text)
    text = cls.read()
    assert text == expected


@pytest.mark.parametrize(
    'name, value, expected',
    [('a', '31', 'root.a = 31'), ('P::Main/a1', '(12, 46)', 'root.a1[0] = 12\nroot.a1[1] = 46')],
)
def test_on_set(first_p1, name: str, value: str, expected: str):
    _, _, mf = first_p1
    cls = TestPyHG(mf, 'P::Main')
    # fixed alias for a
    cls.on_alias(0, 0, 'a', 'P::Main/a')
    pyhg.on_set(cls, 12, 46, name, value)
    text = cls.read()
    assert text == expected


@pytest.mark.parametrize(
    # options = (name, value, sustain, tol, global_tol)
    'options, expected',
    [
        (('P::Main/v', '81', '', '', ''), 'thgrt.check("v", 81)'),
        (('P::Main/v', '(12, 46)', '', '', ''), 'thgrt.check("v[0]", 12)\nthgrt.check("v[1]", 46)'),
        (('v1', '0.9', '', '', '0.1'), 'thgrt.check("v1", 0.9, tolerance=0.1)'),
        (('v1', '0.9', '', '0.5', '0.1'), 'thgrt.check("v1", 0.9, tolerance=0.5)'),
        (('v1', '0.9', '', '', '0.1r'), 'thgrt.check("v1", 0.9, tolerance=-0.1)'),
        (('v1', '0.9', '', '', '0.1%'), 'thgrt.check("v1", 0.9, tolerance=-0.1)'),
        (('v1', '0.9', '', '0.5r', '0.1'), 'thgrt.check("v1", 0.9, tolerance=-0.5)'),
        (('v1', '0.9', '', '0.5%', ''), 'thgrt.check("v1", 0.9, tolerance=-0.5)'),
        (('P::Main/v2', 'true', 'forever', '', ''), 'thgrt.check("v2", True, sustain=-1)'),
        (('P::Main/v2', 'true', '31', '', ''), 'thgrt.check("v2", True, sustain=31)'),
    ],
)
def test_on_check(first_p1, options: tuple[str, str, str, str, str], expected: str):
    _, _, mf = first_p1
    cls = TestPyHG(mf, 'P::Main')
    # fixed alias for v1
    pyhg.on_alias(cls, 2, 3, 'v1', 'P::Main/v1')
    name, value, sustain, tol, global_tol = options
    if global_tol:
        pyhg.on_set_tol(cls, 0, 0, name, '0', global_tol)
    pyhg.on_check(cls, 12, 46, name, value, sustain, '0', tol, filter='')
    text = cls.read()
    assert text == expected


@pytest.mark.parametrize(
    # options = (name, value, sustain, tol, global_tol)
    'name, value, expected',
    [
        ('P::Main/v', '31', 'thgrt.uncheck("v")'),
        ('v1', '(8.1, 8.2)', 'thgrt.uncheck("v1[0]")\nthgrt.uncheck("v1[1]")'),
    ],
)
def test_on_uncheck(first_p1, name: str, value: str, expected: str):
    _, _, mf = first_p1
    cls = TestPyHG(mf, 'P::Main')
    # fixed alias for v1
    pyhg.on_alias(cls, 2, 3, 'v1', 'P::Main/v1')
    pyhg.on_check(cls, 9, 65, name, value, '', '0', '', '')
    text = cls.read()
    pyhg.on_uncheck(cls, 31, 32, name)
    text = cls.read()
    assert text == expected


# on_set_tol tested together with on_check
# def test_on_set_tol(...):


@pytest.mark.parametrize(
    # options = (name, value, sustain, tol, global_tol)
    'name, value, expected',
    [
        ('P::Main/a', '9', 'root.a = 9'),
        ('P::Main/v', '31', 'thgrt.check("v", 31)'),
        ('P::Main/x', '99', ''),
    ],
)
def test_on_set_or_check(first_p1, name: str, value: str, expected: str, capsys):
    _, _, mf = first_p1
    cls = TestPyHG(mf, 'P::Main')
    # fixed alias for v1
    text = cls.read()
    pyhg.on_alias(cls, 2, 3, 'v1', 'P::Main/v1')
    text = cls.read()
    assert not text
    capsys.readouterr()
    pyhg.on_set_or_check(cls, 12, 46, name, value)
    text = cls.read()
    if expected:
        assert text == expected
    else:
        # error
        captured = capsys.readouterr()
        text = captured.out
        assert text[: len('Error:')] == 'Error:'


# on_set_tol tested together with on_set and on_check
# def test_on_alias(...):


def test_main(first_p1, tmpdir):
    # basic test for PyHG.main: since th ecalls to thg are stubbed,
    # the test only verify the call creates the expected files and returns.
    project, procedure, _ = first_p1
    expected = tmpdir / 'p1_nominal.py'
    assert not expected.exists()
    pyhg.thg_main(
        'PYHG2',
        project,
        find_configuration(project, 'KCG'),  # unused
        procedure,
        str(Path(__file__).parent / 'First' / 'Model' / 'KCG'),
        str(tmpdir),
        '-module_name first',
        '-runtime_class my_module.MyRuntime',
    )
    assert expected.exists()
