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

"""Provides a proxy to the ``thg`` module for unit testing."""

try:
    # this module is dynamic and exists only during the execution of SCADE THG
    import thg as _thg
except ModuleNotFoundError:
    # unit tests
    _thg = None


def open(pathname: str, is_init: bool, client_data: object) -> bool:
    """
    Request THG to open a scenario for reading.

    Parameters
    ----------
    pathname : str
        Pathname of the scenario.
    is_init : bool
        Whether the scenario is an initialization scenario.
    client_data : object
        User specific data passed to callback methods.

    Returns
    -------
    bool
        Whether the function open is successful.
    """
    return _thg.open(pathname, is_init, client_data) if _thg else True


def parse() -> bool:
    """
    Request THG to parse a new line/column of the opened scenario.

    This has the effect of calling the appropriate user defined callback
    method.

    Returns
    -------
    bool
        False when the end of the parsed scenario is reached, True otherwise.
    """
    return _thg.parse() if _thg else False


def close():
    """Request THG to close the scenario."""
    if _thg:
        _thg.close()
