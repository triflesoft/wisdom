from .circled import discover_circled
from .circled import generate_circled
from .relative_path import discover_relative_path
from .relative_path import generate_relative_path

JINJA2_DISCOVER_FILTERS = {
    'circled': discover_circled,
    'relative_path': discover_relative_path,
}

JINJA2_GENERATE_FILTERS = {
    'circled': generate_circled,
    'relative_path': generate_relative_path,
}

__all__ = (
    'JINJA2_DISCOVER_FILTERS',
    'JINJA2_GENERATE_FILTERS',
)
