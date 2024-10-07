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

"""SCADE Test Harness Generator for Python."""

from io import TextIOBase
from keyword import iskeyword
import os
from pathlib import Path
from shutil import copy
from typing import Union

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
    def __init__(self, *args, **kwargs):
        # names
        self.module = None
        self.class_ = None
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
        kcg_target_dir: str,
        target_dir: str,
        *args: str,
    ):
        # module name
        if len(args) > 1:
            assert args[0] == '-module_name'
            self.module = args[1]
        else:
            self.module = Path(project.pathname).stem.lower()

        self.procedure = procedure
        # template for target file
        target_file = Path(target_dir) / 'fake.ext'
        # remove the status file, is exists
        status_file = target_file.with_name('thg_files.txt').as_posix()
        try:
            os.unlink(status_file)
        except BaseException:
            pass
        # list of generated files
        generated_files = []

        # load the kcg mapping data from kcg generation directory
        mapping = c.open_mapping((Path(kcg_target_dir) / 'mapping.xml').as_posix())

        # search the mapping data for the procedure's operator
        operator_path = procedure.operator
        if operator_path[-1] != '/':
            operator_path += '/'
        operators = [
            op for op in mapping.get_all_operators() if op.get_scade_path() == operator_path
        ]
        if len(operators) != 1:
            print(operator_path + ': Operator not found within the following ones:')
            print('\t' + '\n\t'.join([op.get_scade_path() for op in mapping.get_all_operators()]))
            return
        operator = operators[0]
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
            target_scenario = target_file.with_name(
                ('%s_%s.py' % (procedure.name, record.name)).lower()
            )
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

        # copy the thgrt lib module
        self.thgrt_file_src = Path(__file__).parent / 'lib' / 'thgrt.py'
        copy(self.thgrt_file_src, Path(target_dir))
        # generate the status file
        with open(status_file, 'w', newline='\n') as fd:
            print('\n'.join(generated_files), file=fd)

    def on_cycle(self, line: int, col: int, number: str):
        # print("cycle: {0} {1} {2}".format(line, col, number))
        if number != '':
            cycles = int(number)
        else:
            cycles = 1
        self.writeln('thgrt.cycle({})'.format(cycles))

    def on_comment(self, line: int, col: int, text: str):
        # print("comment: {0} {1} {2}".format(line, col, text))
        # filter empty comment: parameter always empty with CSV
        if text != '#':
            self.writeln(text)

    def on_set_tol(self, line: int, col: int, dip: str, int_tol: str, real_tol: str):
        # print("set tol: {0} {1} {2} {3} {4}".format(line, col, dip, int_tol, real_tol))
        self.tolerances[dip] = real_tol

    def on_set(self, line: int, col: int, dip: str, value: object):
        # print("set: {0} {1} {2} {3}".format(line, col, dip, value))
        name = self.resolve_io(dip)
        name = self.filter_keyword(name)
        for suffix, literal in flatten(value):
            self.writeln('root.%s%s = %s' % (name, suffix, literal))

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
        if real_tol:
            args += f', tolerance={real_tol}'
        if filter_:
            args += f', filter_={filter_}'
        name = self.resolve_io(dip)
        name = self.filter_keyword(name)
        flatten_names = []
        for suffix, literal in flatten(value):
            flatten_name = name + suffix
            self.writeln(f'thgrt.check("{flatten_name}", {literal}{args})')
            flatten_names.append(flatten_name)
        self.flatten_checks[dip] = flatten_names

    def on_uncheck(self, line: int, col: int, dip: str):
        # print("uncheck: {0} {1} {2}".format(line, col, dip))
        for flatten_name in self.flatten_checks.get(dip, []):
            self.writeln(f'thgrt.uncheck("{flatten_name}")')

    def on_set_or_check(self, line: int, col: int, dip: str, value: object):
        path = self.aliases.get(dip, dip)
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
        # print("alias: {0} {1} {2} {3}".format(line, col, alias, dip))
        self.aliases[alias] = dip

    def on_alias_value(self, line: int, col: int, alias: str, value: object):
        print('alias_value: {0} {1} {2} {3}'.format(line, col, alias, value))
        assert False
        pass

    def on_notify(self, line: int, col: int, msg: str):
        # print("notify: {0} {1} {2}".format(line, col, msg))
        pass

    def on_error(self, line: int, col: int, msg: str):
        print('error: {0} {1} {2}'.format(line, col, msg))
        pass

    def start_scenario(self):
        assert self.procedure
        self.writeln('# generated by %s' % banner)
        self.writeln('')
        self.writeln('from %s import %s' % (self.module, self.class_))
        self.writeln('from thgrt import Thgrt')
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
        self.writeln('thgrt.close()')
        self.writeln('# end of file')

    def writeln(self, text: str):
        assert self.f
        self.f.write(text)
        self.f.write('\n')

    def is_input(self, io: str) -> bool:
        return True if io in self.inputs or io in self.sensors else False

    def is_output(self, io: str) -> bool:
        return True if io in self.outputs or io in self.probes else False

    def init_ios(self, mapping, operator: m.Operator):
        # gather all the names in a dictionary
        for io in operator.get_inputs():
            self.inputs[io.get_scade_path()] = io.get_name()
        for io in operator.get_outputs():
            self.outputs[io.get_scade_path()] = io.get_name()
        # TODO: retrieve sensors and probes from the mapping
        self.sensors = {}
        self.probes = {}
        # print(self.inputs)
        # print(self.outputs)

    def resolve_io(self, name: str) -> str:
        io = self.aliases.get(name, name)
        if io in self.inputs:
            return self.inputs[io]
        elif io in self.outputs:
            return self.outputs[io]
        elif io in self.sensors:
            return self.sensors[io]
        elif io in self.probes:
            return self.probes[io]
        else:
            # TODO: consider the default as probes?
            # rationale: THG already checks the names are valid
            print('%s: unknown I/O' % name)
            return '<%s>' % name

    def filter_keyword(self, name: str) -> str:
        return '{}_'.format(name) if iskeyword(name) else name


# ---------------------------------------------------------------------------
# SCADE Test generators
# ---------------------------------------------------------------------------


def gen_container_records(container):
    for element in container.test_elements:
        if isinstance(element, Record):
            yield element
        else:
            # must be a folder
            yield from gen_container_records(element)


def gen_procedure_records(procedure):
    yield from gen_container_records(procedure)


def gen_record_scenarios(record):
    for scenario in record.inits:
        yield scenario, True
    for scenario in record.preambles:
        yield scenario, False
    for scenario in record.scenarios:
        yield scenario, False


# ---------------------------------------------------------------------------
# naming
# ---------------------------------------------------------------------------


def get_model_module_name(project: Project):
    # name of the proxy Python file
    return Path(project.pathname).stem.lower()


def get_class_name(operator: m.Operator):
    # name of the operator, without package prefix
    return operator.get_name()


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
    str_args: str = '',
):
    # display some banner
    print(banner)

    args = str_args.split()
    PyHG().main(target, project, configuration, procedure, kcg_target_dir, target_dir, *args)


# ---------------------------------------------------------------------------
# raw callbacks for THG
# ---------------------------------------------------------------------------


def on_cycle(client_data: PyHG, line: int, col: int, number: str):
    client_data.on_cycle(line, col, number)


def on_comment(client_data: PyHG, line: int, col: int, text: str):
    client_data.on_comment(line, col, text)


def on_set_tol(client_data: PyHG, line: int, col: int, dip: str, int_tol: str, real_tol: str):
    client_data.on_set_tol(line, col, dip, int_tol, real_tol)


def on_set(client_data: PyHG, line: int, col: int, dip: str, value: object):
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
    client_data.on_check(line, col, dip, value, sustain, int_tol, real_tol, filter)


def on_uncheck(client_data: PyHG, line: int, col: int, dip: str):
    client_data.on_uncheck(line, col, dip)


def on_set_or_check(client_data: PyHG, line: int, col: int, dip: str, value: object):
    client_data.on_set_or_check(line, col, dip, value)


def on_alias(client_data: PyHG, line: int, col: int, alias: str, dip: str):
    client_data.on_alias(line, col, alias, dip)


def on_alias_value(client_data: PyHG, line: int, col: int, alias: str, value: object):
    client_data.on_alias_value(line, col, alias, value)


def on_notify(client_data: PyHG, line: int, col: int, msg: str):
    client_data.on_notify(line, col, msg)


def on_error(client_data: PyHG, line: int, col: int, msg: str):
    client_data.on_error(line, col, msg)
