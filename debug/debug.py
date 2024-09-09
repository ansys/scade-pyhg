# Copyright (C) 2020 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""Main for debugging the extension."""

# product search paths
# C:\Program Files\ANSYS Inc\v251\SCADE\SCADE\APIs\Python\lib
# C:\Program Files\ANSYS Inc\v251\SCADE\SCADE\bin
# debug search paths
# O:\SCADE\APIs\Python\lib
# O:\Suite\x64 - Release

import argparse
import os

from ansys.scade.apitools import declare_project
from ansys.scade.apitools.info import get_scade_home

# apitools must be imported before using any scade.* import
# to make sure sys.path is set properly and scade_env is imported
# isort: split

from scade.code.suite.sctoc import raw_tcl

parser = argparse.ArgumentParser(description='Python way for scade -code')
parser.add_argument('-p', '--project', metavar='<Scade project>', help='SCADE Suite', required=True)
parser.add_argument(
    '-c', '--configuration', metavar='<configuration>', help='configuration', required=True
)
parser.add_argument('-t', '--test', metavar='<procedure>', help='test procedure', required=True)
parser.add_argument(
    '-d', '--directory', metavar='<target_dir>', help='target directory', required=True
)
parser.add_argument(
    '-m', '--module', metavar='<module_name>', help='Python module name', required=False
)
options = parser.parse_args()

os.makedirs(options.directory, exist_ok=True)

declare_project(options.project)


os.environ['SCADE'] = str(get_scade_home())
# the code must have been generated prior to the call
raw_tcl('KcgMF init "%s"' % options.configuration)
args = '"%s" "%s" "%s"' % (options.configuration, options.test, options.directory)
if options.module:
    args += ' {-module_name %s}' % options.module
cmd = 'ThgCustom PYHG2 %s' % args
raw_tcl(cmd)

# debug
"""
debug command line
-p tests/First/Model/First.etp -c KCG -t tests/First/Test/P1.stp -d tests/First/Test/Thg -m first
"""
