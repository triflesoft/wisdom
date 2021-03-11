from jinja2 import FileSystemLoader
from jinja2 import PrefixLoader
from jinja2.sandbox import SandboxedEnvironment
from os import makedirs
from os import scandir
from os import stat
from os.path import dirname
from os.path import join
from shutil import copy

from wisdom.jinja2_extensions import JINJA2_GENERATE_EXTENSIONS
from wisdom.jinja2_filters import JINJA2_GENERATE_FILTERS


class Output:
    def __init__(self, arguments, configuration, source):
        self.arguments = arguments
        self.configuration = configuration
        self.source = source

    def generate_jinja2(self):
        jinja2_environments = {}

        for template_component, version_templates in self.source.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    for template in family_templates:
                        if (not self.arguments.changed_only) or template.is_changed:
                            design_name = template.design_name
                            jinja2_environment = jinja2_environments.get(design_name, None)

                            if not jinja2_environment:
                                jinja2_loader = PrefixLoader({
                                    'source': FileSystemLoader(self.arguments.source_path),
                                    'design': FileSystemLoader(join(self.arguments.design_path, design_name, 'generate/templates')),
                                })
                                jinja2_environment = SandboxedEnvironment(
                                    trim_blocks=True,
                                    lstrip_blocks=True,
                                    keep_trailing_newline=True,
                                    extensions=JINJA2_GENERATE_EXTENSIONS,
                                    autoescape=True,
                                    loader=jinja2_loader,
                                    auto_reload=False)
                                jinja2_environment.filters.update(JINJA2_GENERATE_FILTERS)
                                jinja2_environments[design_name] = jinja2_environment

                            jinja2_template = jinja2_environment.get_template(join('source', template.loader_path))
                            output_html = jinja2_template.render({
                                'output_path': self.arguments.output_path,
                                'component': template_component,
                                'version': template_version,
                                'culture': template_culture,
                                'templates': family_templates,
                                'template': template,
                            })
                            makedirs(dirname(template.output_path), exist_ok=True)

                            with open(template.output_path, 'w') as output_file:
                                output_file.write(output_html)

    def generate_static(self):
        directory_dict = {}

        for template_component, version_templates in self.source.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    for template in family_templates:
                        design_name = template.design_name

                        if design_name not in directory_dict:
                            directory_dict[design_name] = join(self.arguments.design_path, design_name, 'generate/documents')

        static_paths = {}
        directory_queue = []

        for static_path in directory_dict.values():
            directory_queue.append((len(static_path) + 1, static_path))

        while directory_queue:
            root_prefix_length, root_path = directory_queue.pop()

            for directory_entry in scandir(root_path):
                if directory_entry.is_dir(follow_symlinks=False):
                    directory_queue.append((root_prefix_length, directory_entry.path))
                elif directory_entry.is_file(follow_symlinks=False):
                    source_path = directory_entry.path
                    output_path = join(self.arguments.output_path, directory_entry.path[root_prefix_length:])
                    static_paths[output_path] = source_path

        for document_component, name_documents in self.source.documents.items():
            for document in name_documents:
                if (not self.arguments.changed_only) or document.is_changed:
                    static_paths[document.output_path] = document.source_path

        for output_path, source_path in static_paths.items():
            is_changed = True

            try:
                output_stat = stat(output_path)
                source_stat = stat(source_path)
                output_time_ns = max(output_stat.st_ctime_ns, output_stat.st_mtime_ns)
                source_stat_ns = max(source_stat.st_ctime_ns, source_stat.st_mtime_ns)

                is_changed = (output_time_ns <= source_stat_ns) or (output_stat.st_size != source_stat.st_size)
            except:
                pass

            if is_changed:
                makedirs(dirname(output_path), exist_ok=True)
                copy(source_path, output_path)


__all__ = [
    'Output',
]