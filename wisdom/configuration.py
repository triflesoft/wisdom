from logging import debug
from logging import error
from logging import info
from os.path import expanduser
from os.path import join
from re import compile
from sys import exit
from typing import Optional
from yaml import safe_load


class Version:
    def __init__(self, index: int, code: str, name: str, prev_version):
        self.index = index
        self.code = code
        self.name = name
        self.prev_version = prev_version
        self.next_version = None

        if self.prev_version:
            self.prev_version.next_version = self

    def __repr__(self):
        return f'Version(code="{self.code}", name="{self.name}")'


class Culture:
    def __init__(self, index: int, code: str, name: str):
        self.index = index
        self.code = code
        self.name = name

    def __repr__(self):
        return f'Culture(code="{self.code}", name="{self.name}")'


class Component:
    def __init__(
        self,
        index: int,
        code: str,
        design_name: str,
        template_path_pattern: str,
        document_path_pattern: str,
        variables: dict):
        self.index = index
        self.code = code
        self.design_name = design_name
        self.template_path_pattern = compile(template_path_pattern) if template_path_pattern else None
        self.document_path_pattern = compile(document_path_pattern) if document_path_pattern else None
        self.variables = variables

        if 'output_path' not in self.template_path_pattern.groupindex:
            error('Mandatory group "output_path" is missing from template_path_pattern in component "%s".', code)
            exit(1)

        if 'name' not in self.template_path_pattern.groupindex:
            error('Mandatory group "name" is missing from template_path_pattern in component "%s".', code)
            exit(1)

        if 'version' not in self.template_path_pattern.groupindex:
            error('Mandatory group "version" is missing from template_path_pattern in component "%s".', code)
            exit(1)

        if 'culture' not in self.template_path_pattern.groupindex:
            error('Mandatory group "culture" is missing from template_path_pattern in component "%s".', code)
            exit(1)

        if 'output_path' not in self.document_path_pattern.groupindex:
            error('Mandatory group "output_path" is missing from document_path_pattern in component "%s".', code)
            exit(1)

    def __repr__(self):
        return f'Component(code="{self.code}", design_name="{self.design_name}")'


class Configuration:
    def __init__(self, arguments):
        self.versions = {}
        self.cultures = {}
        self.components = {}

        config_paths = [
            '/etc/wisdom/wisdom-cli.yaml',
            expanduser('~/.wisdom-cli.yaml'),
            join(arguments.source_path, 'wisdom-cli.yaml')
        ]

        configuration = {}

        for config_path in config_paths:
            try:
                with open(config_path, 'r') as config_file:
                    configuration.update(safe_load(config_file))

                debug(f'Merged configuration from "{config_path}".')
            except:
                debug(f'Failed reading configuration from "{config_path}".')

        if 'versions' not in configuration:
            error('Configuration defines no versions.')
            exit(1)

        if 'cultures' not in configuration:
            error('Configuration defines no cultures.')
            exit(1)

        version: Optional[Version] = None

        for index, (code, config) in enumerate(configuration['versions'].items()):
            version = Version(index, code, config['name'], version)
            self.versions[version.code] = version

        for index, (code, config) in enumerate(configuration['cultures'].items()):
            culture = Culture(index, code, config['name'])
            self.cultures[culture.code] = culture

        for index, (code, config) in enumerate(configuration['components'].items()):
            component = Component(
                index,
                code,
                config.get('design_name', 'default'),
                config.get('template_path_pattern', None),
                config.get('document_path_pattern', None),
                config.get('variables', {}))
            self.components[component.code] = component


__all__ = [
    'Configuration'
]