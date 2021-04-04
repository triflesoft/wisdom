from jinja2 import FileSystemLoader
from jinja2 import PrefixLoader
from jinja2.sandbox import SandboxedEnvironment
from os.path import dirname
from os.path import join

from .extensions import JINJA2_DISCOVER_EXTENSIONS
from .extensions import JINJA2_GENERATE_EXTENSIONS
from .filters import JINJA2_DISCOVER_FILTERS
from .filters import JINJA2_GENERATE_FILTERS


class EnvironmentBase(SandboxedEnvironment):
    def __init__(self, source_path, design_path, output_path, extensions, filters):
        super().__init__(
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            extensions=extensions,
            autoescape=True,
            loader=PrefixLoader({
                'design': FileSystemLoader(design_path),
                'source': FileSystemLoader(source_path),
            }),
            auto_reload=False
        )
        self.filters.update(filters)
        self.globals['design_path'] = design_path
        self.globals['source_path'] = source_path
        self.globals['output_path'] = output_path

    def join_path(self, template, parent):
        if ':' in template:
            parts = template.split(':', 1)
            return join(parts[0], dirname(parent), parts[1])

        return template


class DiscoverEnvironment(EnvironmentBase):
    def __init__(self, source_path, design_path, output_path):
        super().__init__(source_path, design_path, output_path, JINJA2_DISCOVER_EXTENSIONS, JINJA2_DISCOVER_FILTERS)


class GenerateEnvironment(EnvironmentBase):
    def __init__(self, source_path, design_path, output_path):
        super().__init__(source_path, design_path, output_path, JINJA2_GENERATE_EXTENSIONS, JINJA2_GENERATE_FILTERS)


__all__ = ('DiscoverEnvironment', 'GenerateEnvironment')
