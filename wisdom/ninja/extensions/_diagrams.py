from base64 import b64encode
from copy import deepcopy
from hashlib import sha512
from os import makedirs
from os.path import dirname
from os.path import isfile
from os.path import join
from importlib import import_module
from pkgutil import iter_modules
from re import compile
from sys import modules
from urllib.parse import quote

from .base import embed_extension

from diagrams import Diagram
from diagrams import Cluster


class Globals:
    pass


def build_globals_level_2(module_path, import_path):
    obj = Globals()

    for submodule_info in iter_modules([module_path]):
        if submodule_info.ispkg:
            subobj = build_globals_level_2(
                join(module_path, submodule_info.name),
                f'{import_path}.{submodule_info.name}')
        else:
            submodule = import_module(f'{import_path}.{submodule_info.name}')
            subobj = Globals()

            for class_name in dir(submodule):
                if not class_name.startswith('_') and class_name[0].isupper():
                    print(f'{import_path[9:]}.{submodule_info.name}.{class_name}("{import_path[9:]}.{submodule_info.name}.{class_name}")')
                    setattr(subobj, class_name, getattr(submodule, class_name))

        setattr(obj, submodule_info.name, subobj)

    return obj

def build_globals_level_1():
    diagrams_module_path = dirname(modules[Diagram.__module__].__file__)
    diagrams_import_path = 'diagrams'
    result = {}

    for submodule_info in iter_modules([diagrams_module_path]):
        if submodule_info.ispkg:
            result[submodule_info.name] = build_globals_level_2(
                join(diagrams_module_path, submodule_info.name),
                f'{diagrams_import_path}.{submodule_info.name}')

    result['Cluster'] = Cluster

    return result


EVAL_LOCALS = build_globals_level_1()
XLINK_HREF = compile('xlink\:href=\"([^\"]+\.png)"')


class DiagramsDiscoverExtension(embed_extension('DiagramsDiscoverExtensionBase', 'diagrams')):
    def _process_markup(self, context, source_path, source_line, caller, content_path=None, description='Diagrams Diagram', format='png'):
        return ''


class DiagramsGenerateExtension(embed_extension('DiagramsGenerateExtensionBase', 'diagrams')):
    def _process_markup(self, context, source_path, source_line, caller, content_path=None, description='Diagrams Diagram', format='png'):
        content_text = None

        if content_path:
            with open(content_path, 'r', newline='') as content_file:
                content_text = content_file.read()
        else:
            content_text = str(caller())

        diagram_markup_data = content_text.encode('utf-8')
        diagram_hash = sha512()
        diagram_hash.update(diagram_markup_data)
        image_name = diagram_hash.hexdigest()
        output_path = context['output_path']
        diagrams_prefix = context['component'].variables.get('diagrams_output_prefix', 'static/images/diagrams').strip('/')

        local_name = join(output_path, diagrams_prefix, image_name)
        local_path = join(output_path, diagrams_prefix, f'{image_name}.{format}')
        image_link = join(diagrams_prefix, f'{image_name}.{format}')

        if not isfile(local_path):
            makedirs(dirname(local_path), exist_ok=True)

            with Diagram(filename=local_name, outformat=format, show=False, graph_attr={'dpi': '48'}):
                exec(content_text, globals(), deepcopy(EVAL_LOCALS))

            if format == 'svg':
                with open(local_path, 'r') as svg_file:
                    svg_text_input = svg_file.read()

                svg_text_output = []
                svg_text_last_index = 0
                png_data_urls = {}

                for match in XLINK_HREF.finditer(svg_text_input):
                    match_start = match.start(0)
                    match_end = match.end(0)

                    if match_start > svg_text_last_index:
                        svg_text_output.append(svg_text_input[svg_text_last_index:match_start])

                    svg_text_output.append('href=\"data:image/png;base64,')

                    png_path = match.group(1)
                    png_data_url = png_data_urls.get(png_path)

                    if not png_data_url:
                        with open(png_path, 'rb') as png_file:
                            png_data_url = b64encode(png_file.read()).decode('ascii')
                            png_data_urls[png_path] = png_data_url

                    svg_text_output.append(png_data_url)
                    svg_text_output.append('\"')
                    svg_text_last_index = match_end

                svg_text_output.append(svg_text_input[svg_text_last_index:])

                with open(local_path, 'w') as svg_file:
                    svg_file.write(''.join(svg_text_output))

        return f'''
<figure class="illustration-outer illustration-diagrams">
    <button class="original-code-copy" data-original-code="{quote(content_text)}">
        <img class="original-code-copy" src="static/images/icon-figure-code-copy.svg" alt="" />
    </button>
    <img class="illustration-inner" src="{image_link}" alt="{description}" />
    <figcaption class="illustration-inner">{description}</figcaption>
</figure>'''
