# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
import sys

import pytest
from scade.code.suite.mapping import c
import scade.model.project.stdproject as std
import scade.model.testenv as qte

import ansys.scade.pyhg.pyhg as pyhg
from conftest import load_project, load_test_application


@pytest.fixture(scope='session')
def first_models() -> tuple[std.Project, qte.TestApplication, c.MappingFile]:
    """Load the project."""
    path = Path(__file__).parent / 'First' / 'Test' / 'Test.etp'
    project = load_project(path)
    application = load_test_application(project)
    kcg_target_dir = Path(__file__).parent / 'First' / 'Model' / 'KCG'
    mf = c.open_mapping((kcg_target_dir / 'mapping.xml').as_posix())
    return project, application, mf


@pytest.mark.parametrize(
    'name, expected',
    [('P1', {'Nominal'})],
)
def test_gen_procedure_records(first_models, name, expected):
    _, application, _ = first_models
    for procedure in application.procedures:
        if procedure.name == name:
            break
    else:
        assert False
    records = {_.name for _ in pyhg.gen_procedure_records(procedure)}
    assert records == expected


@pytest.mark.parametrize(
    'path, expected',
    [('P1.Nominal', {'MainInit.sss', 'Preamble.sss', 'MainNominal.sss'})],
)
def test_gen_record_scenarios(first_models, path, expected):
    _, application, _ = first_models
    procedure_name, record_name = path.split('.')
    for procedure in application.procedures:
        if procedure.name == procedure_name:
            break
    else:
        assert False
    for record in procedure.records:
        if record.name == record_name:
            break
    else:
        assert False
    scenarios = {Path(r.pathname).name for r, _ in pyhg.gen_record_scenarios(record)}
    assert scenarios == expected


@pytest.mark.parametrize(
    'name, expected',
    [('state', 'state'), ('class', 'class_')],
)
def test_filter_keyword(first_models, name: str, expected: str):
    cls = pyhg.PyHG()
    new_name = cls.filter_keyword(name)
    assert new_name == expected


@pytest.mark.parametrize(
    'path, expected',
    [('P::Main', 'Main_P'), ('P::Main/', 'Main_P'), ('Q::Main', '')],
)
def test_get_operator(first_models, path, expected, capsys):
    _, _, mf = first_models
    cls = pyhg.PyHG()
    # clean the output
    capsys.readouterr()
    operator = cls.get_operator(mf, path)
    if not operator:
        assert not expected
        captured = capsys.readouterr()
        assert captured.out
    else:
        assert operator.get_generated().get_name() == expected


@pytest.mark.parametrize(
    'io_path, kind, expected',
    # TODO: add at least sensors
    [('P::Main/a', 'I', 'a'), ('P::Main/v', 'O', 'v')],
)
def test_ios(first_models, io_path: str, kind: str, expected: str):
    # kind: I (input) | O (output) | S (sensor) | P (probe)
    _, _, mf = first_models
    cls = pyhg.PyHG()
    operator = cls.get_operator(mf, 'P::Main/')
    assert operator
    cls.init_ios(mf, operator)
    io = cls.resolve_io(io_path)
    assert io == expected
    if kind == 'I' or kind == 'S':
        assert cls.is_input(io_path)
    if kind == 'O' or kind == 'P':
        assert cls.is_output(io_path)


@pytest.mark.parametrize(
    'text, expected',
    [('a', 'a\n'), ('b\n\tc\nd', 'b\n\tc\nd\n')],
)
def test_writeln(text: str, expected: str, capsys):
    cls = pyhg.PyHG()
    assert isinstance(sys.stdout, io.TextIOBase)
    cls.f = sys.stdout
    # clear output
    capsys.readouterr()
    cls.writeln(text)
    captured = capsys.readouterr()
    assert captured.out == expected
