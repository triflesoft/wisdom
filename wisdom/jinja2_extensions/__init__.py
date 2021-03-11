from .graphviz import GraphvizDiscoverExtension
from .graphviz import GraphvizGenerateExtension
from .markdown import MarkDownDiscoverExtension
from .markdown import MarkDownGenerateExtension
from .plantuml import PlantUmlDiscoverExtension
from .plantuml import PlantUmlGenerateExtension
from .pygments import PygmentsDiscoverExtension
from .pygments import PygmentsGenerateExtension

JINJA2_DISCOVER_EXTENSIONS = (
    'jinja2.ext.do',
    'jinja2.ext.loopcontrols',
    GraphvizDiscoverExtension,
    MarkDownDiscoverExtension,
    PlantUmlDiscoverExtension,
    PygmentsDiscoverExtension)

JINJA2_GENERATE_EXTENSIONS = (
    'jinja2.ext.do',
    'jinja2.ext.loopcontrols',
    GraphvizGenerateExtension,
    MarkDownGenerateExtension,
    PlantUmlGenerateExtension,
    PygmentsGenerateExtension)

__all__ = (
    'JINJA2_DISCOVER_EXTENSIONS',
    'JINJA2_GENERATE_EXTENSIONS',
)
