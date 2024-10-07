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

"""Unit tests utils."""

from pathlib import Path

# note: importing apitools modifies sys.path to access SCADE APIs
import ansys.scade.apitools  # noqa: F401

# must be imported after apitools
# isort: split
import scade
import scade.model.project.stdproject as std
import scade.model.testenv as qte


def load_test_application(project: std.Project) -> qte.TestApplication:
    """Create an instance of TestApplication instance and its procedures."""
    application = qte.TestApplication()
    for file in project.file_refs:
        if Path(file.pathname).suffix.lower() == '.stp':
            application.load_procedure_tcl(file.pathname)
    return application


def load_project(path: Path) -> std.Project:
    """
    Load a Scade project in a separate environment.

    Note: Undocumented API.
    """
    project = scade.load_project(str(path))
    return project


def find_configuration(project: std.Project, name: str) -> std.Configuration:
    for configuration in project.configurations:
        if configuration.name == name:
            return configuration
    assert False


def find_procedure(application: qte.TestApplication, name: str) -> qte.Procedure:
    for procedure in application.procedures:
        if procedure.name == name:
            return procedure
    assert False
