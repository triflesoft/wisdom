from collections import defaultdict
from html.parser import HTMLParser
from itertools import chain
from jinja2 import FileSystemLoader
from jinja2 import PrefixLoader
from jinja2.sandbox import SandboxedEnvironment
from logging import error
from logging import warning
from os import scandir
from os import stat
from os.path import basename
from os.path import join
from re import compile
from re import DOTALL
from typing import Optional
from yaml import safe_load

from wisdom.arguments import Arguments
from wisdom.configuration import Component
from wisdom.configuration import Configuration
from wisdom.configuration import Version
from wisdom.configuration import Culture
from wisdom.jinja2_extensions import JINJA2_DISCOVER_EXTENSIONS
from wisdom.jinja2_filters import JINJA2_DISCOVER_FILTERS


class Template:
    def __init__(
            self,
            source_path: str,
            output_path: str,
            output_link: str,
            loader_path: str,
            timestamp_ns: int,
            is_changed: bool,
            component: Component,
            family: str,
            version: Optional[Version],
            culture: Optional[Culture],
            design_name: str,
            variables: dict):
        self.source_path = source_path
        self.output_path = output_path
        self.output_link = output_link
        self.loader_path = loader_path
        self.timestamp_ns = timestamp_ns
        self.is_changed = is_changed
        self.component = component
        self.family = family
        self.version = version
        self.culture = culture
        self.design_name = design_name
        self.variables = variables
        self.version_mutations = []
        self.culture_mutations = []
        self.parent = None
        self.ancestors = []
        self.prev_sibling = None
        self.next_sibling = None
        self.children = []
        self.toc = []

    def __repr__(self):
        return f'Template(component="{self.component.code}", loader_path="{self.loader_path}", version="{self.version.name if self.version else "*"}", culture="{self.culture.name if self.culture else "*"}")'


class TemplateToc:
    def __init__(self, name: str, attr_id: str, title: str):
        self.name = name
        self.attr_id = attr_id
        self.title = title
        self.children = []

    def __repr__(self):
        return f'TemplateToc(name="{self.name}", attr_id="{self.attr_id}", title="{self.title}")'


class TemplateTocDiscoveryParser(HTMLParser):
    TAG_LEVELS = {
        'h1': 1,
        'h2': 2,
        'h3': 3,
        'h4': 4,
        'h5': 5,
        'h6': 6,
    }

    def __init__(self, source_path: str):
        super().__init__()
        self.source_path = source_path
        self.tag_stats = defaultdict(int)
        self.active_tag_name = None
        self.active_tag_title = None
        self.active_tag_attr_id = None
        self.last_tag_level = 0
        self.attr_ids = set()
        self.toc = []
        self.ancestors = []

    def handle_starttag(self, name: str, attrs: list):
        if self.active_tag_name:
            error(
                'Template "%s" TOC is inconsistent, tag <%s> cannot have children, but tag <%s> was found inside it.',
                self.source_path,
                self.active_tag_name,
                name)
            raise RuntimeError()
        else:
            if name in self.TAG_LEVELS:
                self.active_tag_name = name
                self.active_tag_attr_id = dict(attrs).get('id', '')

                if not self.active_tag_attr_id:
                    error(
                        'Template "%s" TOC is inconsistent, tag <%s> has not id attribute specified.',
                        self.source_path,
                        self.active_tag_name)
                    raise RuntimeError()

                if self.active_tag_attr_id in self.attr_ids:
                    error(
                        'Template "%s" TOC is inconsistent, tag <%s id="%d"> has non-unique id attribute specified.',
                        self.source_path,
                        self.active_tag_name,
                        self.active_tag_attr_id)
                    raise RuntimeError()

                if len(self.toc) > 0:
                    if self.TAG_LEVELS[self.active_tag_name] - self.last_tag_level > 1:
                        error(
                            'Template "%s" TOC is inconsistent, tag <%s id="%s"> follows tag <%s id="%s">.',
                            self.source_path,
                            self.active_tag_name,
                            self.active_tag_attr_id,
                            self.toc[-1].name,
                            self.toc[-1].attr_id)
                        raise RuntimeError()

                self.last_tag_level = self.TAG_LEVELS[self.active_tag_name]

    def handle_endtag(self, name: str):
        if self.active_tag_name:
            if name != self.active_tag_name:
                error(
                    'Template "%s" TOC is inconsistent, tag </%s> was closed, but <%s> was previously open.',
                    self.source_path,
                    name,
                    self.active_tag_name)
                raise RuntimeError()
            else:
                while (len(self.ancestors) > 0) and (self.TAG_LEVELS[self.ancestors[-1].name] >= self.TAG_LEVELS[self.active_tag_name]):
                    self.ancestors.pop()

                if len(self.ancestors) == 0:
                    self.toc.append(TemplateToc(self.active_tag_name, self.active_tag_attr_id, self.active_tag_title))
                    self.ancestors.append(self.toc[-1])
                else:
                    self.ancestors[-1].children.append(TemplateToc(self.active_tag_name, self.active_tag_attr_id, self.active_tag_title))
                    self.ancestors.append(self.ancestors[-1].children[-1])

                self.tag_stats[self.active_tag_name] += 1
                self.active_tag_name = None
                self.active_tag_attr_id = None
                self.active_tag_title = None

    def handle_data(self, data: str):
        self.active_tag_title = data


class Document:
    def __init__(
            self,
            preprocessor: str,
            source_path: str,
            output_path: str,
            loader_path: str,
            timestamp_ns: int,
            is_changed: bool,
            component: Component):
        self.preprocessor = preprocessor
        self.source_path = source_path
        self.output_path = output_path
        self.loader_path = loader_path
        self.timestamp_ns = timestamp_ns
        self.is_changed = is_changed
        self.component = component

    def __repr__(self):
        return f'Document(component="{self.component.code}", loader_path="{self.loader_path}")'


class SourceDiscovery:
    def __init__(self, arguments, configuration):
        self.arguments = arguments
        self.configuration = configuration
        self.templates = {}
        self.template_version_mutations = {}
        self.template_culture_mutations = {}
        self.template_version_custom_mutations = {}
        self.template_culture_custom_mutations = {}
        self.documents = {}

        for component in chain(self.configuration.components.values(), (None, )):
            component_templates = {}

            for version in chain(self.configuration.versions.values(), (None, )):
                version_templates = {}

                for culture in chain(self.configuration.cultures.values(), (None, )):
                    version_templates[culture] = {}

                component_templates[version] = version_templates

            self.templates[component] = component_templates
            self.template_version_mutations[component] = defaultdict(lambda : defaultdict(dict))
            self.template_culture_mutations[component] = defaultdict(lambda : defaultdict(dict))
            self.documents[component] = {}

    def discover(self):
        directory_queue = [(len(self.arguments.source_path) + 1, self.arguments.source_path)]
        comment_pattern = compile('[ \t\r\n]*{#[\r\n](?P<comment>.*?[\r\n])#}[\r\n]', DOTALL)
        template_file_paths = []
        document_file_paths = []

        while directory_queue:
            root_prefix_length, root_path = directory_queue.pop()

            for directory_entry in scandir(root_path):
                if directory_entry.is_dir(follow_symlinks=False):
                    directory_queue.append((root_prefix_length, directory_entry.path))
                elif directory_entry.is_file(follow_symlinks=False):
                    source_path = directory_entry.path
                    loader_path = directory_entry.path[root_prefix_length:]

                    for component in self.configuration.components.values():
                        if component.template_path_pattern:
                            match = component.template_path_pattern.fullmatch(loader_path)

                            if match:
                                output_path = join(self.arguments.output_path, match.group('output_path'))
                                template_file_paths.append((source_path, loader_path, output_path, directory_entry.stat(), component, match.groupdict()))
                                break

                        if component.document_path_pattern:
                            match = component.document_path_pattern.fullmatch(loader_path)

                            if match:
                                output_path = join(self.arguments.output_path, match.group('output_path'))
                                document_file_paths.append((source_path, loader_path, output_path, directory_entry.stat(), component))
                                break

        directory_queue = []
        design_set = set()

        for component in self.configuration.components.values():
            if not component.design_name in design_set:
                design_set.add(component.design_name)
                design_path = join(self.arguments.design_path, component.design_name, 'generate/documents')
                directory_queue.append((len(design_path) + 1, design_path))

        while directory_queue:
            root_prefix_length, root_path = directory_queue.pop()

            for directory_entry in scandir(root_path):
                if directory_entry.is_dir(follow_symlinks=False):
                    directory_queue.append((root_prefix_length, directory_entry.path))
                elif directory_entry.is_file(follow_symlinks=False):
                    source_path = directory_entry.path

                    if (
                        source_path.endswith('.css') or
                        source_path.endswith('.jpg') or
                        source_path.endswith('.js') or
                        source_path.endswith('.png') or
                        source_path.endswith('.sass') or
                        source_path.endswith('.scss') or
                        source_path.endswith('.svg') or
                        source_path.endswith('.txt')):
                        loader_path = directory_entry.path[root_prefix_length:]
                        output_path = join(self.arguments.output_path, loader_path)
                        document_file_paths.append((source_path, loader_path, output_path, directory_entry.stat(), None))

        template_file_paths = sorted(template_file_paths, key=lambda fp: fp[1], reverse=True)

        while template_file_paths:
            source_path, loader_path, output_path, source_stat, component, match_dict = template_file_paths.pop()
            output_link = match_dict['output_path'].lstrip('/')
            family = match_dict['family']
            version = match_dict['version']
            culture = match_dict['culture']
            source_timestamp_ns = max(source_stat.st_ctime_ns, source_stat.st_mtime_ns)
            variables = {
                'title': basename(family).title(),
                'outline': None
            }
            version_custom_mutations = {}
            culture_custom_mutations = {}

            if source_stat.st_size > 8:
                with open(source_path, 'r') as template_file:
                    template_text = template_file.read(4096)
                    comment_match = comment_pattern.match(template_text)

                    if comment_match:
                        try:
                            template_config = safe_load(comment_match.group('comment'))
                            mutations = template_config.get('mutations', None)

                            variables.update(template_config.get('variables', {}))

                            if mutations:
                                version_custom_mutations = mutations.get('version', {})
                                culture_custom_mutations = mutations.get('culture', {})
                        except:
                            warning('First comment of template "%s" is not a valid YAML.', source_path)

            is_changed = True

            try:
                output_stat = stat(output_path)
                output_timestamp_ns = max(output_stat.st_ctime_ns, output_stat.st_mtime_ns)

                if output_timestamp_ns >source_timestamp_ns:
                    is_changed = False
            except:
                pass

            template = Template(
                source_path,
                output_path,
                output_link,
                loader_path,
                source_timestamp_ns,
                is_changed,
                component,
                family,
                self.configuration.versions[version] if version else None,
                self.configuration.cultures[culture] if culture else None,
                component.design_name,
                variables)

            self.template_version_custom_mutations[template.source_path] = version_custom_mutations
            self.template_culture_custom_mutations[template.source_path] = culture_custom_mutations
            self.templates[template.component][template.version][template.culture][template.family] = template

            if template.version:
                self.template_version_mutations[template.component][template.family][template.culture][template.version] = template

            if template.culture:
                self.template_culture_mutations[template.component][template.family][template.version][template.culture] = template

        document_file_paths = sorted(document_file_paths, key=lambda fp: fp[1], reverse=True)

        while document_file_paths:
            source_path, loader_path, output_path, source_stat, component = document_file_paths.pop()
            source_name = basename(source_path)
            preprocessor = None

            if source_name.startswith('_'):
                continue
            elif source_path.endswith('.sass'):
                preprocessor = 'sass'
                output_path = output_path[:-4] + 'css'
            elif source_path.endswith('.scss'):
                preprocessor = 'scss'
                output_path = output_path[:-4] + 'css'

            source_timestamp_ns = max(source_stat.st_ctime_ns, source_stat.st_mtime_ns)
            is_changed = True

            try:
                output_stat = stat(output_path)
                output_timestamp_ns = max(output_stat.st_ctime_ns, output_stat.st_mtime_ns)

                if output_timestamp_ns >source_timestamp_ns:
                    is_changed = False
            except:
                pass

            document = Document(
                preprocessor,
                source_path,
                output_path,
                loader_path,
                source_timestamp_ns,
                is_changed,
                component)

            self.documents[document.component][document.loader_path] = document

    def apply_custom_version_mutations(self):
        for template_component, version_templates in self.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    for template_family, template in family_templates.items():
                        for version_code, mutation_family in self.template_version_custom_mutations[template.source_path].items():
                            try:
                                mutation_version = self.configuration.versions[version_code]
                            except KeyError:
                                error(
                                    'Template "%s" references invalid version "%s" for mutation "%s".',
                                    template.source_path,
                                    version_code,
                                    mutation_family)
                                raise RuntimeError()

                            try:
                                mutation = self.templates[template_component][mutation_version][template_culture][mutation_family]
                            except KeyError:
                                error(
                                    'Template "%s" references invalid mutation "%s" for version "%s".',
                                    template.source_path,
                                    mutation_family,
                                    version_code)
                                raise RuntimeError()

                            self.template_version_mutations[template_component][template_family][template_culture][mutation_version] = mutation
                            self.template_version_mutations[mutation.component][mutation.family][mutation.culture][template_version] = template

    def apply_custom_culture_mutations(self):
        for template_component, version_templates in self.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    for template_family, template in family_templates.items():
                        for culture_code, mutation_family in self.template_culture_custom_mutations[template.source_path].items():
                            try:
                                mutation_culture = self.configuration.cultures[culture_code]
                            except KeyError:
                                error(
                                    'Template "%s" references invalid culture "%s" for mutation "%s".',
                                    template.source_path,
                                    culture_code,
                                    mutation_family)
                                raise RuntimeError()

                            try:
                                mutation = self.templates[template_component][template_version][mutation_culture][mutation_family]
                            except KeyError:
                                error(
                                    'Template "%s" references invalid mutation "%s" for culture "%s".',
                                    template.source_path,
                                    mutation_family,
                                    culture_code)
                                raise RuntimeError()

                            self.template_culture_mutations[template_component][template.family][template_version][mutation_culture] = mutation
                            self.template_culture_mutations[mutation.component][mutation.family][mutation.version][template_culture] = template

    def sort_templates(self):
        for template_component, version_templates in self.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    for template_family, template in family_templates.items():
                        template.version_mutations = sorted(self.template_version_mutations[template.component][template.family][template_culture].items(), key=lambda i: i[0].index)
                        template.culture_mutations = sorted(self.template_culture_mutations[template.component][template.family][template.version].items(), key=lambda i: i[0].index)

    def calculate_template_hierarchy(self):
        for template_component, version_templates in self.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    family_templates = dict(sorted(family_templates.items(), key=lambda kv: kv[0]))
                    hierarchy = family_templates.values()
                    prev_template = None

                    for template in hierarchy:
                        parent_template = prev_template

                        while parent_template:
                            if template.family.startswith(parent_template.family):
                                template.parent = parent_template

                                if template.variables['outline'] and parent_template.variables["outline"]:
                                    template.variables['outline'] = f'{parent_template.variables["outline"]}.{template.variables["outline"]}'
                                else:
                                    template.variables['outline'] = ''

                                parent_template.children.append(template)

                                while parent_template:
                                    template.ancestors.append(parent_template)
                                    parent_template = parent_template.parent

                                template.ancestors = list(reversed(template.ancestors))
                                break

                            parent_template = parent_template.parent
                        prev_template = template

    def calculate_template_numbering(self):
        for template_component, version_templates in self.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    for template_family, template in family_templates.items():
                        for index in range(0, len(template.children) - 1):
                            template.children[index].next_sibling = template.children[index + 1]
                            template.children[index + 1].prev_sibling = template.children[index]

    def calculate_template_toc(self):
        jinja2_environments = {}

        for template_component, version_templates in self.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    for template_family, template in family_templates.items():
                        if template.source_path.endswith('.html.j2'):
                            if (not self.arguments.changed_only) or template.is_changed:
                                design_name = template.design_name
                                jinja2_environment = jinja2_environments.get(design_name, None)

                                if not jinja2_environment:
                                    jinja2_loader = PrefixLoader({
                                        'source': FileSystemLoader(self.arguments.source_path),
                                        'design': FileSystemLoader(join(self.arguments.design_path, design_name, 'discover/templates')),
                                    })
                                    jinja2_environment = SandboxedEnvironment(
                                        trim_blocks=True,
                                        lstrip_blocks=True,
                                        keep_trailing_newline=True,
                                        extensions=JINJA2_DISCOVER_EXTENSIONS,
                                        autoescape=True,
                                        loader=jinja2_loader,
                                        auto_reload=False)
                                    jinja2_environment.filters.update(JINJA2_DISCOVER_FILTERS)
                                    jinja2_environments[design_name] = jinja2_environment

                                jinja2_template = jinja2_environment.get_template(join('source', template.loader_path))
                                output_html = jinja2_template.render({'this': template})
                                toc_parser = TemplateTocDiscoveryParser(template.source_path)
                                toc_parser.feed(output_html)

                                if toc_parser.tag_stats['h1'] == 0:
                                    warning(
                                        'Template "%s" TOC is inconsistent, no <h1> tag was found.',
                                        template.source_path)
                                elif toc_parser.tag_stats['h1'] >= 2:
                                    warning(
                                        'Template "%s" TOC is inconsistent, too many <h1> tags was found.',
                                        template.source_path)

                                template.toc = toc_parser.toc


class Source:
    def __init__(self, arguments: Arguments, configuration: Configuration):
        self.arguments = arguments
        self.configuration = configuration
        self.templates = defaultdict(lambda : defaultdict(lambda : defaultdict(list)))
        self.documents = {}

    def discover(self):
        source_discovery = SourceDiscovery(self.arguments, self.configuration)
        source_discovery.discover()
        source_discovery.apply_custom_version_mutations()
        source_discovery.apply_custom_culture_mutations()
        source_discovery.sort_templates()
        source_discovery.calculate_template_hierarchy()
        source_discovery.calculate_template_numbering()
        source_discovery.calculate_template_toc()

        for template_component, version_templates in source_discovery.templates.items():
            for template_version, culture_templates in version_templates.items():
                for template_culture, family_templates in culture_templates.items():
                    templates = sorted(family_templates.values(), key=lambda t: str(t.variables['outline']))

                    for template in templates:
                        template.children = sorted(template.children, key=lambda t: str(t.variables['outline']))

                    if template_version is None:
                        for version in self.configuration.versions.values():
                            self.templates[template_component][version][template_culture] += templates
                    else:
                        self.templates[template_component][template_version][template_culture] += templates

        for document_component, name_documents in source_discovery.documents.items():
            documents = sorted(name_documents.values(), key=lambda d: d.loader_path)

            self.documents[document_component] = documents


__all__ = [
    'Source',
]
