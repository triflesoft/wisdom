from .admonition import AdmonitionDiscoverExtension
from .admonition import AdmonitionGenerateExtension
from .aside import AsideGenerateExtension
from .data_table import DataTableDiscoverExtension
from .data_table import DataTableGenerateExtension
from .graphviz import GraphvizDiscoverExtension
from .graphviz import GraphvizGenerateExtension
from .markdown import MarkDownDiscoverExtension
from .markdown import MarkDownGenerateExtension
from .page import PageDiscoverExtension
from .page import PageGenerateExtension
from .plantuml import PlantUmlDiscoverExtension
from .plantuml import PlantUmlGenerateExtension
from .pygments import PygmentsDiscoverExtension
from .pygments import PygmentsGenerateExtension
from .section import SectionGenerateExtension


JINJA2_DISCOVER_EXTENSIONS = (
    'jinja2.ext.do',
    'jinja2.ext.loopcontrols',
    AdmonitionDiscoverExtension,
    AsideGenerateExtension,
    DataTableDiscoverExtension,
    GraphvizDiscoverExtension,
    MarkDownDiscoverExtension,
    PageDiscoverExtension,
    PlantUmlDiscoverExtension,
    PygmentsDiscoverExtension,
    SectionGenerateExtension
)


JINJA2_GENERATE_EXTENSIONS = (
    'jinja2.ext.do',
    'jinja2.ext.loopcontrols',
    AdmonitionGenerateExtension,
    AsideGenerateExtension,
    DataTableGenerateExtension,
    GraphvizGenerateExtension,
    MarkDownGenerateExtension,
    PageGenerateExtension,
    PlantUmlGenerateExtension,
    PygmentsGenerateExtension,
    SectionGenerateExtension,
)


__all__ = (
    'JINJA2_DISCOVER_EXTENSIONS',
    'JINJA2_GENERATE_EXTENSIONS',
)
