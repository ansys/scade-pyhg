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

"""Settings page for SCADE Test THG."""

import scade
from scade.model.project.stdproject import Configuration, Project
from scade.tool.suite.gui.settings import Page as SettingsPage
from scade.tool.suite.gui.widgets import EditBox, Label, Widget

from ansys.scade.pyhg import TARGET

# ---------------------------------------------------------------------------
# globals
# ---------------------------------------------------------------------------

# default value, for compatibility with TCL pages
H_EDIT = 20
H_LABEL = 20

# position / size for labels of the first columns
xl1 = 17
wl1 = 140
# position / size for fields of the first columns
xf1 = 160
wf1 = 190
# space between two lines
dy = 30

# ---------------------------------------------------------------------------
# reusable control library
# ---------------------------------------------------------------------------

TOOL = 'QTE'


class LabelEditBox(EditBox):
    """Label and EditBox in the same line."""

    def __init__(self, owner, text: str, wl: int, x=10, y=10, w=50, h=14, **kwargs):
        """Initialize the control."""
        self.label = Label(owner, text, x=x, y=y + 4, w=wl, h=H_LABEL)
        super().__init__(owner, x=x + wl, y=y, w=w - wl, h=H_EDIT, **kwargs)
        self.owner = owner

    def on_layout(self):
        """Layout the control."""
        self.set_constraint(Widget.RIGHT, self.owner, Widget.RIGHT, -xl1)


class PageUtils:
    """Utilities for settings pages."""

    def __init__(self):
        """Initialize the utilities."""
        scade.output('initialized controls\n')
        # self.controls = []

    def add_edit(self, y: int, text: str) -> EditBox:
        """Add an edit box."""
        edit = LabelEditBox(self, text, wl1, x=xl1, y=y, w=wl1 + wf1)
        self.controls.append(edit)
        return edit

    def layout_controls(self):
        """Layout the controls."""
        for control in self.controls:
            control.on_layout()


class SettingsPageEx(SettingsPage, PageUtils):
    """Extended settings page."""

    def __init__(self, *args):
        """Initialize the page."""
        super(PageUtils, self).__init__()
        super().__init__(*args)
        # runtime properties
        self.controls = []

    def on_layout(self):
        """Layout the page."""
        self.layout_controls()

    def on_close(self):
        """Close the page."""
        pass


# ---------------------------------------------------------------------------
# settings pages
# ---------------------------------------------------------------------------

TITLE = 'Python Test Environment'


class SettingsPagePyHG(SettingsPageEx):
    """Settings page for Python HG."""

    def __init__(self):
        """Initialize the page."""
        super().__init__(TITLE)

        # controls
        self.ed_module = None
        self.ed_rt = None

    def on_build(self):
        """Build the page."""
        # alignment for the first line
        y = 10

        self.ed_module = self.add_edit(y, '&Module name:')
        y += dy

        self.ed_rt = self.add_edit(y, '&Runtime class:')
        y += dy

    def on_display(self, project: Project, configuration: Configuration):
        """Display the page."""
        value = project.get_scalar_tool_prop_def(TARGET, 'P1', '', configuration)
        assert self.ed_module
        self.ed_module.set_name(value)
        value = project.get_scalar_tool_prop_def(TARGET, 'P2', '', configuration)
        if not value:
            # can't be empty
            value = 'ansys.scade.pyhg.lib.thgrt.Thgrt'
        assert self.ed_rt
        self.ed_rt.set_name(value)

    def on_validate(self, project: Project, configuration: Configuration):
        """Validate the page."""
        # command line
        values = []
        # properties
        assert self.ed_module
        value = self.ed_module.get_name()
        project.set_scalar_tool_prop_def(TARGET, 'P1', value, '', configuration)
        values.extend(['-module_name', value] if value else [])
        assert self.ed_rt
        value = self.ed_rt.get_name()
        project.set_scalar_tool_prop_def(TARGET, 'P2', value, '', configuration)
        values.extend(['-runtime_class', value] if value else [])
        # summary for THG
        project.set_tool_prop_def(TOOL, 'TARGET_%s' % TARGET, values, [], configuration)


# ---------------------------------------------------------------------------
# GUI items
# ---------------------------------------------------------------------------

SettingsPagePyHG()
