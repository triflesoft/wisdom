from ._admonition import AdmonitionGenerateExtension
from ._aside import AsideGenerateExtension
from ._data_table import DataTableDiscoverExtension
from ._data_table import DataTableGenerateExtension
from ._diagrams import DiagramsDiscoverExtension
from ._diagrams import DiagramsGenerateExtension
from ._graphviz import GraphvizDiscoverExtension
from ._graphviz import GraphvizGenerateExtension
from ._markdown import MarkDownGenerateExtension
from ._page import PageDiscoverExtension
from ._page import PageGenerateExtension
from ._plantuml import PlantUmlDiscoverExtension
from ._plantuml import PlantUmlGenerateExtension
from ._pygments import PygmentsDiscoverExtension
from ._pygments import PygmentsGenerateExtension
from ._section import SectionGenerateExtension


JINJA2_DISCOVER_EXTENSIONS = (
    'jinja2.ext.do',
    'jinja2.ext.loopcontrols',
    AdmonitionGenerateExtension,
    AsideGenerateExtension,
    DataTableDiscoverExtension,
    DiagramsDiscoverExtension,
    GraphvizDiscoverExtension,
    MarkDownGenerateExtension,
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
    DiagramsGenerateExtension,
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
