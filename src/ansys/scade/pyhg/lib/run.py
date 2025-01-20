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

"""Template for running all the tests from a directory hierarchy."""

import importlib
from pathlib import Path
import sys

tests = {}
tests_result = True


def run_all(dir: Path):
    """Run all the scenarios in the directory."""
    scenarios = list(Path(dir).glob('*.py'))
    for scenario in scenarios:
        global tests, tests_result
        print('\nrun {}:\n'.format(scenario.name))
        scenario_module_name = dir.stem + '.' + scenario.stem
        scenario_module = importlib.import_module(scenario_module_name)
        tests[scenario.name] = scenario_module.thgrt.test_result
        tests_result = tests_result and scenario_module.thgrt.test_result


if __name__ == '__main__':
    script_dir = Path(__file__).parent

    if sys.argv[1:]:
        scenario_dir = script_dir.joinpath(*sys.argv[1:])
    else:
        scenario_dir = script_dir / 'scenarios'

    # add scenarios dir in path for thgrt.py
    sys.path.append(str(scenario_dir))

    # all tests header
    print('\n##################################')
    print('Run all scenarios in: {}'.format(scenario_dir))
    print('##################################\n')

    # run all the scenarios found in arv[1], default to './scenarios'
    run_all(scenario_dir)

    # all tests bottom
    print('\n##################################')
    print('Tests result: {}'.format('passed' if tests_result else 'failed'))
    print('\nPassed scenario:')
    for scenario, result in tests.items():
        if result:
            print('    {}'.format(scenario))
    if not tests_result:
        print('\nFailed scenarios:')
        for scenario, result in tests.items():
            if not result:
                print('    {}'.format(scenario))
    print('##################################')
