from jinja2 import escape
from logging import error
from os.path import join
from os.path import normpath

from .base import include_extension


class PageDiscoverExtension(include_extension('PageDiscoverExtensionBase', 'page')):
    def _process_markup(
            self,
            context,
            source_path,
            source_line,
            caller,
            relative_path=None,
            absolute_path=None):
        return f'<a class="nav-internal" href=""></a>'


class PageGenerateExtension(include_extension('PageGenerateExtensionBase', 'page')):
    def _process_markup(
            self,
            context,
            source_path,
            source_line,
            caller,
            relative_path=None,
            absolute_path=None):
        this = context['this']
        templates = context['templates']

        if absolute_path is not None:
            if ':' in absolute_path:
                component_code, template_family = absolute_path.split(':', 1)
            else:
                component_code, template_family = this.component.code, absolute_path
        elif relative_path is not None:
            if ':' in relative_path:
                component_code, template_family = relative_path.split(':', 1)
            else:
                component_code, template_family = this.component.code, relative_path

            template_family = normpath(join(this.family, template_family))
        else:
            error(
                'Document "%s:%d" contains invalid page reference. Either absolute_path, or relative_path must be specified.',
                source_path,
                source_line)

            raise RuntimeError()

        for template in templates:
            if (template.component.code == component_code) and (template.family == template_family):
                title = template.variables['title']
                parent = template.parent

                while parent:
                    title = f'{parent.variables["title"]} / {title}'
                    parent = parent.parent

                return f'<a class="nav-internal" href="{template.output_link}">{escape(title)}</a>'

        error(
            'Document "%s:%d" contains invalid page reference. Path "%s" cannot be resolved.',
            source_path,
            source_line,
            template_family)

        raise RuntimeError()
