# Copyright (C) 2020 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Tests the integration with SCADE Test and verifies the outputs of the produced script."""

import os
from pathlib import Path
import shutil
import subprocess
import sys

import ansys.scade.apitools.info as info
from conftest import diff_files, run

_test_dir = Path(__file__).parent


def _run_scade(*args) -> subprocess.CompletedProcess:
    """Run scade.exe in a subprocess."""
    venv = Path(sys.executable).parent.parent.as_posix()
    print('setting VIRTUAL_ENV to', venv)
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = venv
    cmd = [str(info.get_scade_home() / 'SCADE' / 'bin' / 'scade.exe')]
    cmd.extend([str(_) for _ in args])
    status = run(cmd, env)
    return status


def test_integration(tmpdir):
    """Test the integration with SCADE Test and verify the outputs of the produced script."""
    # tmpdir: replace LocalPath by Path
    tmpdir = Path(tmpdir)
    version = info.get_scade_version()
    if version < 261:
        print(f'test skipped: requires at least SCADE 2026 R1 (current: v{sys.version})')
        return
    if version == 261:
        print(
            'test skipped: SCADE 2026 R1 Test Harness Generator '
            'does not support virtual environments'
        )
        return

    # copy the model and test files
    def copy_files(src: Path, dst: Path):
        dst.mkdir()
        for entry in src.glob('*'):
            if entry.is_file():
                shutil.copyfile(entry, dst / entry.name)

    first_dir = _test_dir / 'First'
    print('copying model and tests to', tmpdir)
    for directory in ['Model', 'Test']:
        copy_files(first_dir / directory, tmpdir / directory)

    model = tmpdir / 'Model' / 'First.etp'
    print('build the wrapper')
    status = _run_scade('-code', model, '-conf', 'Python', '-sim')
    assert status.returncode == 0
    print('generate the code')
    status = _run_scade('-code', model, '-conf', 'KCG')
    assert status.returncode == 0
    print('generate the Python harness')
    test = tmpdir / 'Test' / 'Test.etp'
    status = _run_scade('-test', test, '-thg', '-conf', 'Test')
    assert status.returncode == 0
    # set PYTHONPATH to the generation dir
    env = os.environ.copy()
    env['PYTHONPATH'] = str(first_dir / 'Model' / 'Python')
    for name in ['p1_nominal', 'p1_realspecial']:
        script = tmpdir / 'Test' / 'Thg' / f'{name}.py'
        cmd = [sys.executable, script]
        status = run(cmd, env)
        assert status.returncode == 0
        ref = _test_dir / 'ref' / f'{name}.txt'
        res = tmpdir / ref.name
        res.write_text(status.stdout.decode('utf-8').replace('\r', ''))
        assert not diff_files(res, ref)
