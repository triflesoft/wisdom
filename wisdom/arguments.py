from argparse import ArgumentParser
from os.path import abspath
from os.path import dirname
from os.path import isdir
from os.path import join
from os.path import normpath
from sys import argv
from sys import exit
from sys import stderr


class Arguments:
    def _parse(self):
        default_design_path = join(dirname(argv[0]), 'design')
        argument_parser = ArgumentParser()
        argument_parser.add_argument(
            '-s', '--source',
            default='./source/',
            metavar='/PATH/TO/SOURCE/',
            help='Path to source files.')
        argument_parser.add_argument(
            '-d', '--design',
            action='store',
            default=default_design_path,
            metavar='/PATH/TO/DESIGN/',
            help='Path to design files.')
        argument_parser.add_argument(
            '-o', '--output',
            action='store',
            default='./output/',
            metavar='/PATH/TO/OUTPUT/',
            help='Path to output files.')
        argument_parser.add_argument(
            '-c', '--changed-only',
            action='store_true',
            help='Regenerate output files for changed source files only. Compares timestamps.')
        argument_parser.add_argument(
            '-w', '--watch',
            action='store',
            default=None,
            const=True,
            nargs='?',
            metavar='/PATH/TO/WATCH/',
            help='Continuously watch a directory for changes and regenerate output. Watches source directory by default. Also specify --changed-only option for better performance.')
        argument_parser.add_argument(
            '-v', '--verbose',
            action='count',
            default=0,
            help='Increase output verbosity.')
        self._arguments = argument_parser.parse_args()

    def _check(self):
        if self._arguments.watch is True:
            self._arguments.watch = self._arguments.source

        paths = {
            'source': {
                'original': self._arguments.source,
                'normalized': normpath(abspath(self._arguments.source)),
            },
            'design': {
                'original': self._arguments.design,
                'normalized': normpath(abspath(self._arguments.design)),
            },
            'output': {
                'original': self._arguments.output,
                'normalized': normpath(abspath(self._arguments.output)),
            },
        }

        if self._arguments.watch:
            paths['watch'] = {
                'original': self._arguments.watch,
                'normalized': normpath(abspath(self._arguments.watch)),
            }

        for parameter_name, values in paths.items():
            if not isdir(values['normalized']):
                print(f'Argument "{parameter_name}"" is specified as "{values["original"]}" and resolved into "{values["normalized"]}" must be a directory.', file=stderr)
                exit(1)

        for parameter_name, values in paths.items():
            if self._arguments.verbose >= 1:
                print(f'Argument "{parameter_name}"" is specified as "{values["original"]}" and resolved into "{values["normalized"]}".')

            setattr(self._arguments, parameter_name, values['normalized'])

    def __init__(self):
        self._parse()
        self._check()

    @property
    def source_path(self):
        return self._arguments.source

    @property
    def design_path(self):
        return self._arguments.design

    @property
    def output_path(self):
        return self._arguments.output

    @property
    def changed_only(self):
        return self._arguments.changed_only

    @property
    def watch_path(self):
        return self._arguments.watch

    @property
    def verbosity_level(self):
        return self._arguments.verbose


__all__ = [
    'Arguments',
]
