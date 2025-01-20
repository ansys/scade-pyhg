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

"""SCADE Test Harness Generator for Python."""

from io import TextIOBase
from keyword import iskeyword
from pathlib import Path
import re
from typing import Optional, Union

from scade.code.suite.mapping import c, model as m
from scade.model.project.stdproject import Configuration, Project
from scade.model.testenv import Procedure, Record

from ansys.scade.pyhg import __version__
import ansys.scade.pyhg.proxy_thg as thg
from ansys.scade.pyhg.values import flatten

# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

banner = 'PyHG ' + __version__


class PyHG:
    """Python Harness Generator."""

    def __init__(self, *args, **kwargs):
        """Initialize the generator."""
        # names
        self.module = ''
        self.runtime = 'ansys.scade.pyhg.lib.thgrt.Thgrt'
        self.class_ = ''
        self.procedure = None
        # path -> name
        self.inputs = {}
        self.outputs = {}
        self.sensors = {}
        self.probes = {}
        # alias -> path
        self.aliases = {}
        # output file descriptor
        self.f: Union[None, TextIOBase] = None
        # flatten names for a single check
        self.flatten_checks = {}
        # tolerances
        self.tolerances = {}

    def main(
        self,
        target: str,
        project: Project,
        configuration: Configuration,
        procedure: Procedure,
        kcg_target_dir: Path,
        target_dir: Path,
        *args: str,
    ):
        """Generate the test harness for the procedure."""
        # options
        for arg in args:
            param, value = arg.split(maxsplit=1)
            if param == '-module_name':
                self.module = value
            elif param == '-runtime_class':
                self.runtime = value

        if not self.module:
            self.module = Path(project.pathname).stem.lower()

        self.procedure = procedure
        # remove the status file, is exists
        status_file = target_dir / 'thg_files.txt'
        status_file.unlink(missing_ok=True)
        # list of generated files
        generated_files = []

        # load the kcg mapping data from kcg generation directory
        mapping = c.open_mapping((Path(kcg_target_dir) / 'mapping.xml').as_posix())

        # search the mapping data for the procedure's operator
        operator = self.get_operator(mapping, procedure.operator)
        if not operator:
            return
        # class for the operator
        name = operator.get_name()
        self.class_ = name[0].upper() + name[1:]
        # init the io dictionary
        self.init_ios(mapping, operator)

        # process the records: dump the semantic actions from the callbacks
        # (above on_xxx functions)
        for record in gen_procedure_records(procedure):
            print(
                '=== record {0} for {1}/{2}'.format(
                    record.name,
                    operator.get_generated().get_header_name(),
                    operator.get_generated().get_name(),
                )
            )
            # assume one generated file per record
            target_scenario = target_dir / ('%s_%s.py' % (procedure.name, record.name)).lower()
            with target_scenario.open('w') as self.f:
                self.start_scenario()
                for scenario, is_init in gen_record_scenarios(record):
                    pathname = scenario.pathname
                    # if thg.open(pathname, is_init, self.f):
                    if thg.open(pathname, is_init, self):
                        while thg.parse():
                            pass
                        thg.close()
                self.close_scenario()
            generated_files.append(target_scenario.name)

        # generate the status file
        with status_file.open('w', newline='\n') as fd:
            print('\n'.join(generated_files), file=fd)

    def on_cycle(self, line: int, col: int, number: str):
        """Call the cycle action."""
        # print("cycle: {0} {1} {2}".format(line, col, number))
        if number != '':
            cycles = int(number)
        else:
            cycles = 1
        self.writeln('thgrt.cycle({})'.format(cycles))

    def on_comment(self, line: int, col: int, text: str):
        """Call the comment action."""
        # print("comment: {0} {1} {2}".format(line, col, text))
        # filter empty comment: parameter always empty with CSV
        if text != '#':
            self.writeln(text)

    def on_set_tol(self, line: int, col: int, dip: str, int_tol: str, real_tol: str):
        """Call the set_tol action."""
        # print("set tol: {0} {1} {2} {3} {4}".format(line, col, dip, int_tol, real_tol))
        self.tolerances[dip] = real_tol

    def on_set(self, line: int, col: int, dip: str, value: object):
        """Call the set action."""
        # print("set: {0} {1} {2} {3}".format(line, col, dip, value))
        io, projection = self.split_io(dip)
        path = self.aliases.get(io, io)
        root = 'sensors' if self.is_sensor(path) else 'root'
        name = self.resolve_io(path)
        name = self.filter_keyword(name)
        for suffix, literal in flatten(value):
            self.writeln('%s.%s%s%s = %s' % (root, name, projection, suffix, literal))

    def on_check(
        self,
        line: int,
        col: int,
        dip: str,
        value: object,
        sustain: str,
        int_tol: str,
        real_tol: str,
        filter_: str,
    ):
        """Call the check action."""
        # print("check: {0} {1} {2} {3} {4} {5} {6} {7}".format(line, col, dip, value, sustain, int_tol, real_tol, filter))
        # register the check
        args = ''
        if sustain == 'forever':
            n_sustain = -1
        elif not sustain:
            n_sustain = 1
        else:
            n_sustain = int(sustain)
        if n_sustain != 1:
            args += f', sustain={n_sustain}'
        if not real_tol:
            real_tol = self.tolerances.get(dip, self.tolerances.get(''))
        arg_tol = f', tolerance={real_tol}' if real_tol else ''
        if filter_:
            args += f', filter_={filter_}'
        io, projection = self.split_io(dip)
        path = self.aliases.get(io, io)
        name = self.resolve_io(path)
        name = self.filter_keyword(name)
        flatten_names = []
        for suffix, literal in flatten(value):
            flatten_name = name + projection + suffix
            if not arg_tol or literal in {'True', 'False'}:
                # no tolerance
                self.writeln(f'thgrt.check("{flatten_name}", {literal}{args})')
            else:
                self.writeln(f'thgrt.check("{flatten_name}", {literal}{args}{arg_tol})')
            flatten_names.append(flatten_name)
        self.flatten_checks[dip] = flatten_names

    def on_uncheck(self, line: int, col: int, dip: str):
        """Call the uncheck action."""
        # print("uncheck: {0} {1} {2}".format(line, col, dip))
        for flatten_name in self.flatten_checks.get(dip, []):
            self.writeln(f'thgrt.uncheck("{flatten_name}")')

    def on_set_or_check(self, line: int, col: int, dip: str, value: object):
        """Call the set_or_check action."""
        io, _ = self.split_io(dip)
        path = self.aliases.get(io, io)
        # print("set or check: {0} {1} {2} {3}".format(line, col, dip, value))
        if self.is_input(path):
            # print("set: {0} {1} {2} {3}".format(line, col, dip, value))
            self.on_set(line, col, dip, value)
        elif self.is_output(path):
            # print("check: {0} {1} {2} {3}".format(line, col, dip, value))
            self.on_check(line, col, dip, value, '', '', '', '')
        else:
            print('Error: on_set_or_check(%s) not an input or output' % dip)

    def on_alias(self, line: int, col: int, alias: str, dip: str):
        """Call the alias action."""
        # print("alias: {0} {1} {2} {3}".format(line, col, alias, dip))
        self.aliases[alias] = dip

    def on_alias_value(self, line: int, col: int, alias: str, value: object):
        """Call the alias_value action."""
        print('alias_value: {0} {1} {2} {3}'.format(line, col, alias, value))
        assert False
        pass

    def on_notify(self, line: int, col: int, msg: str):
        """Call the notify action."""
        # print("notify: {0} {1} {2}".format(line, col, msg))
        pass

    def on_error(self, line: int, col: int, msg: str):
        """Call the error action."""
        print('error: {0} {1} {2}'.format(line, col, msg))
        pass

    # utils

    def start_scenario(self):
        """Write the header of the scenario."""
        assert self.procedure
        self.writeln('# generated by %s' % banner)
        self.writeln('')
        sensors = ', sensors' if self.sensors else ''
        self.writeln('from %s import %s%s' % (self.module, self.class_, sensors))
        # runtime provided as module.class
        path = self.runtime.split('.')
        self.writeln('from %s import %s as Thgrt' % ('.'.join(path[:-1]), path[-1]))
        self.writeln('')
        self.writeln('# instance of root operator')
        self.writeln('root = %s()' % (self.class_))
        self.writeln('')
        self.writeln('# instance of Thgrt')
        self.writeln(
            "thgrt = Thgrt(root, '{}', '{}')".format(self.procedure.operator, self.procedure.name)
        )
        self.writeln('')

    def close_scenario(self):
        """Write the footer of the scenario."""
        self.writeln('thgrt.close()')
        self.writeln('# end of file')

    def writeln(self, text: str):
        """Write a line of text to the output file."""
        assert self.f
        self.f.write(text)
        self.f.write('\n')

    def get_operator(self, mf: c.MappingFile, operator_path: str) -> Optional[m.Operator]:
        """Get the operator from the mapping data."""
        # search the mapping data for the procedure's operator
        if operator_path[-1] != '/':
            operator_path += '/'
        operator = next(
            (op for op in mf.get_all_operators() if op.get_scade_path() == operator_path), None
        )
        if not operator:
            print(operator_path + ': Operator not found within the following ones:')
            print('\t' + '\n\t'.join([op.get_scade_path() for op in mf.get_all_operators()]))
            return None
        return operator

    def is_input(self, io: str) -> bool:
        """Check if the I/O is an input."""
        return io in self.inputs or io in self.sensors

    def is_sensor(self, io: str) -> bool:
        """Check if the I/O is a sensor."""
        return io in self.sensors

    def is_output(self, io: str) -> bool:
        """Check if the I/O is an output."""
        return io in self.outputs or io in self.probes

    def split_io(self, io: str) -> tuple[str, str]:
        """Split the I/O into the path and the projection."""
        m = re.match(r'([^\[\.]*)(.*)', io)
        assert m and len(m.groups()) == 2
        return (m.groups()[0], m.groups()[1])

    def init_ios(self, mf: c.MappingFile, operator: m.Operator):
        """Initialize the I/O dictionaries."""
        # gather all the names in a dictionary
        self.inputs = {_.get_scade_path(): _.get_name() for _ in operator.get_inputs()}
        self.outputs = {_.get_scade_path(): _.get_name() for _ in operator.get_outputs()}
        # remove trailing '/' to be consistent with local variables
        self.sensors = {_.get_scade_path().strip('/'): _.get_name() for _ in mf.get_all_sensors()}
        # TODO: probes from the mapping
        self.probes = {}

    def resolve_io(self, path: str) -> str:
        """Resolve the I/O path to a name."""
        if path in self.inputs:
            return self.inputs[path]
        elif path in self.outputs:
            return self.outputs[path]
        elif path in self.sensors:
            return self.sensors[path]
        elif path in self.probes:
            return self.probes[path]
        else:
            # TODO: consider the default as probes?
            # rationale: THG already checks the names are valid
            print('%s: unknown I/O' % path)
            return '<%s>' % path

    def filter_keyword(self, name: str) -> str:
        """Filter the name to avoid Python keywords."""
        return '{}_'.format(name) if iskeyword(name) else name


# ---------------------------------------------------------------------------
# SCADE Test generators
# ---------------------------------------------------------------------------


def gen_container_records(container):
    """Generate the records from a container."""
    for element in container.test_elements:
        if isinstance(element, Record):
            yield element
        else:
            # must be a folder
            yield from gen_container_records(element)


def gen_procedure_records(procedure):
    """Generate the records from a procedure."""
    yield from gen_container_records(procedure)


def gen_record_scenarios(record):
    """Generate the scenarios from a record."""
    for scenario in record.inits:
        yield scenario, True
    for scenario in record.preambles:
        yield scenario, False
    for scenario in record.scenarios:
        yield scenario, False


# ---------------------------------------------------------------------------
# interface
# ---------------------------------------------------------------------------


def thg_main(
    target: str,
    project: Project,
    configuration: Configuration,
    procedure: Procedure,
    kcg_target_dir: str,
    target_dir: str,
    *args: str,
):
    """Generate the test harness for the procedure."""
    # display some banner
    print(banner)

    PyHG().main(
        target, project, configuration, procedure, Path(kcg_target_dir), Path(target_dir), *args
    )


# ---------------------------------------------------------------------------
# raw callbacks for THG
# ---------------------------------------------------------------------------


def on_cycle(client_data: PyHG, line: int, col: int, number: str):
    """Call the cycle action."""
    client_data.on_cycle(line, col, number)


def on_comment(client_data: PyHG, line: int, col: int, text: str):
    """Call the comment action."""
    client_data.on_comment(line, col, text)


def on_set_tol(client_data: PyHG, line: int, col: int, dip: str, int_tol: str, real_tol: str):
    """Call the set_tol action."""
    client_data.on_set_tol(line, col, dip, int_tol, real_tol)


def on_set(client_data: PyHG, line: int, col: int, dip: str, value: object):
    """Set the values."""
    client_data.on_set(line, col, dip, value)


def on_check(
    client_data: PyHG,
    line: int,
    col: int,
    dip: str,
    value: object,
    sustain: str,
    int_tol: str,
    real_tol: str,
    filter: str,
):
    """Check the values."""
    client_data.on_check(line, col, dip, value, sustain, int_tol, real_tol, filter)


def on_uncheck(client_data: PyHG, line: int, col: int, dip: str):
    """Call the uncheck action."""
    client_data.on_uncheck(line, col, dip)


def on_set_or_check(client_data: PyHG, line: int, col: int, dip: str, value: object):
    """Create a set or check action."""
    client_data.on_set_or_check(line, col, dip, value)


def on_alias(client_data: PyHG, line: int, col: int, alias: str, dip: str):
    """Create an alias."""
    client_data.on_alias(line, col, alias, dip)


def on_alias_value(client_data: PyHG, line: int, col: int, alias: str, value: object):
    """Create an alias value."""
    client_data.on_alias_value(line, col, alias, value)


def on_notify(client_data: PyHG, line: int, col: int, msg: str):
    """Create a notify action."""
    client_data.on_notify(line, col, msg)


def on_error(client_data: PyHG, line: int, col: int, msg: str):
    """Create an error action."""
    client_data.on_error(line, col, msg)
