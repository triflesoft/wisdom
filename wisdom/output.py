from collections import defaultdict
from logging import info
from logging import error
from os import makedirs
from os.path import dirname
from os.path import join
from shutil import copy
from subprocess import run

from wisdom.ninja import GenerateEnvironment


class Output:
    def __init__(self, arguments, configuration, source):
        self.arguments = arguments
        self.configuration = configuration
        self.source = source

    def generate_jinja2(self):
        jinja2_environments = {}

        hierarchy = defaultdict(lambda : defaultdict(list))
        templates = defaultdict(lambda : defaultdict(list))

        for template_component, version_templates in self.source.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    for template in family_templates:
                        if template.parent is None:
                            hierarchy[template_version][template_culture].append(template)

                        templates[template_version][template_culture].append(template)

        for template_component, version_templates in self.source.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    for template in family_templates:
                        if (not self.arguments.changed_only) or template.is_changed:
                            design_name = template.design_name
                            jinja2_environment = jinja2_environments.get(design_name, None)

                            if not jinja2_environment:
                                jinja2_environment = GenerateEnvironment(
                                    self.arguments.source_path,
                                    join(self.arguments.design_path, design_name, 'generate/templates'),
                                    self.arguments.output_path)
                                jinja2_environments[design_name] = jinja2_environment

                            jinja2_template = jinja2_environment.get_template(join('source', template.loader_path))
                            output_html = jinja2_template.render({
                                'component': template_component,
                                'version': template_version,
                                'culture': template_culture,
                                'hierarchy': hierarchy[template_version][template_culture],
                                'templates': templates[template_version][template_culture],
                                'this': template,
                            })
                            makedirs(dirname(template.output_path), exist_ok=True)

                            with open(template.output_path, 'w') as output_file:
                                output_file.write(output_html)

    def generate_static(self):
        static_paths = {}

        for document_component, name_documents in self.source.documents.items():
            for document in name_documents:
                if (not self.arguments.changed_only) or document.is_changed:
                    static_paths[document.output_path] = document

        for output_path, document in static_paths.items():
            makedirs(dirname(output_path), exist_ok=True)

            if document.preprocessor in ('sass', 'scss'):
                info('sass "%s" "%s"', document.source_path, output_path)
                result = run(
                    ['sass', document.source_path, output_path],
                    capture_output=True)

                if result.returncode != 0:
                    error('Document "%s" cannot be processed by SASS.', document.source_path)
                    error(result.stderr.decode('utf-8'))
                    raise RuntimeError()
            else:
                copy(document.source_path, output_path)


__all__ = [
    'Output',
]