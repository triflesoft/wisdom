from hashlib import sha512
from logging import info
from logging import error
from os import makedirs
from os.path import dirname
from os.path import isfile
from os.path import join
from subprocess import run
from urllib.parse import quote

from .base import embed_extension


class GraphvizDiscoverExtension(embed_extension('GraphvizDiscoverExtensionBase', 'graphviz')):
    def _process_markup(self, context, source_path, source_line, caller, content_path=None, description='Graphviz Diagram', format='svg', executable='dot'):
        return ''


class GraphvizGenerateExtension(embed_extension('GraphvizGenerateExtensionBase', 'graphviz')):
    def _process_markup(self, context, source_path, source_line, caller, content_path=None, description='Graphviz Diagram', format='svg', executable='dot'):
        content_text = None

        if content_path:
            with open(content_path, 'r', newline='') as content_file:
                content_text = content_file.read()
        else:
            content_text = str(caller())

        diagram_markup_data = content_text.encode('utf-8')
        diagram_hash = sha512()
        diagram_hash.update(diagram_markup_data)
        image_name = f'{diagram_hash.hexdigest()}.{format}'
        output_path = context['output_path']
        graphviz_prefix = context['component'].variables.get('graphviz_output_prefix', 'static/images/graphviz').strip('/')
        graphviz_executable = context['component'].variables.get(f'graphviz_executable_{executable}', executable)
        local_path = join(output_path, graphviz_prefix, image_name)
        image_link = join(graphviz_prefix, image_name)

        if not isfile(local_path):
            makedirs(dirname(local_path), exist_ok=True)
            info('"%s" -T%s', graphviz_executable, format)
            result = run(
                [graphviz_executable, f'-T{format}'],
                input=diagram_markup_data,
                capture_output=True)

            if result.returncode != 0:
                error(result.stderr.decode('utf-8'))
                error(
                    'Document "%s:%d" contains invalid GraphViz markup.',
                    source_path,
                    source_line)

                raise RuntimeError()

            with open(local_path, 'wb') as image_file:
                image_file.write(result.stdout)

        return f'''
<figure class="illustration-outer illustration-graphviz">
    <button class="original-code-copy" data-original-code="{quote(content_text)}">
        <img class="original-code-copy" src="static/images/icon-figure-code-copy.svg" alt="" />
    </button>
    <img class="illustration-inner" src="{image_link}" alt="{description}" />
    <figcaption class="illustration-inner">{description}</figcaption>
</figure>'''
