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

"""Runtime template for Python teste produced by Python Harness Generator."""


class Check:
    """Check object for THG."""

    def __init__(self, expected: object, sustain: int, tolerance: float, filter_: str):
        """Initialize the check."""
        self.expected = expected
        self.sustain = sustain
        self.tolerance = tolerance
        # not implemented
        self.filter = filter_


class Thgrt:
    """THG runtime."""

    def __init__(self, root: object, operator: str, procedure_name: str):
        """Initialize the runtime."""
        self.step = 1
        self.test_result = True
        self.root = root
        self.operator = operator
        self.procedure_name = procedure_name
        # checks
        self.checks = {}

        print('========================')
        print('Operator: {}'.format(operator))
        print('Procedure: {}\n'.format(procedure_name))

    def close(self):
        """Close the runtime."""
        print('Test result: {}'.format('passed' if self.test_result else 'failed'))
        print('========================')

    def cycle(self, cycles: int):
        """Run the test for a number of cycles."""
        for cycle in range(cycles):
            # print("Step {}".format(self.step))
            self.root.call_cycle()
            self.check_values()
            self.step += 1

    def check(
        self, name: str, expected: object, sustain: int = 1, tolerance: float = 0, filter_: str = ''
    ):
        """Check a value."""
        self.checks[name] = Check(expected, sustain, tolerance, filter_)

    def uncheck(self, name: str):
        """Uncheck a value."""
        try:
            self.checks.pop(name)
        except KeyError as e:
            print(str(e))

    def check_values(self):
        """Check the values."""
        # flush all checks and remove those which are no longer valid
        to_remove = []
        for name, check in self.checks.items():
            value = eval(f'self.root.{name}')

            if check.tolerance:
                delta = value - check.expected
                if delta < 0:
                    delta = -delta
                if delta <= check.tolerance:
                    passed = True
                else:
                    passed = False
            else:
                passed = value == check.expected

            # print only failed checks for clarity
            if not passed:
                self.log_failure(self.step, name, value, check.expected)
            self.test_result = self.test_result and passed

            if check.sustain == 1:
                to_remove.append(name)
            elif check.sustain != -1:
                check.sustain -= 1

        for name in to_remove:
            self.checks.pop(name)

    def log_failure(self, step: int, name: str, value, expected):
        """Log a failure."""
        print(
            'test failed at step {}: {}={} (expected {})'.format(self.step, name, value, expected)
        )
