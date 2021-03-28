from hashlib import sha512
from logging import info
from logging import error
from os import makedirs
from os.path import dirname
from os.path import isfile
from os.path import join
from subprocess import run
from urllib.parse import quote

from .base import discover_content_extension
from .base import generate_content_extension


PlantUmlDiscoverExtension = discover_content_extension('PlantUmlDiscoverExtension', 'plantuml')


class PlantUmlGenerateExtension(generate_content_extension('PlantUmlGenerateExtensionBase', 'plantuml')):
    def _process_markup(self, context, caller, description='PlantUML Diagram', format='svg'):
        diagram_markup_text = str(caller())
        diagram_markup_data = diagram_markup_text.encode('utf-8')
        diagram_hash = sha512()
        diagram_hash.update(diagram_markup_data)
        image_name = f'{diagram_hash.hexdigest()}.{format}'
        output_path = context['output_path']
        plantuml_prefix = context['component'].variables.get('plantuml_output_prefix', 'static/images/plantuml').strip('/')
        plantuml_executable = context['component'].variables.get(f'plantuml_jar', 'plantuml.jar')
        local_path = join(output_path, plantuml_prefix, image_name)
        image_link = join(plantuml_prefix, image_name)

        if not isfile(local_path):
            makedirs(dirname(local_path), exist_ok=True)
            info('java -var "%s" -pipe -failfast2 -T%s', plantuml_executable, format)
            result = run(
                ['java', '-jar', plantuml_executable, '-pipe', '-failfast2', f'-t{format}'],
                input=diagram_markup_data,
                capture_output=True)

            if result.returncode != 0:
                error('Document "%s" contains invalid PlantUML markup.', context['template'].source_path)
                error(result.stderr.decode('utf-8'))
                raise RuntimeError()

            with open(local_path, 'wb') as image_file:
                image_file.write(result.stdout)

        return f'''
<figure class="illustration-outer illustration-plantuml">
    <button class="original-code-copy" data-original-code="{quote(diagram_markup_text)}">
        <img class="original-code-copy" src="static/images/icon-figure-code-copy.svg" alt="" />
    </button>
    <img class="illustration-inner" src="{image_link}" alt="{description}" />
    <figcaption class="illustration-inner">{description}</figcaption>
</figure>'''
