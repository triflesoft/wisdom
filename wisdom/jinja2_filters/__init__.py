from .relative_path import discover_relative_path
from .relative_path import generate_relative_path

JINJA2_DISCOVER_FILTERS = {
    'relative_path': discover_relative_path,
}

JINJA2_GENERATE_FILTERS = {
    'relative_path': generate_relative_path,
}

__all__ = (
    'JINJA2_DISCOVER_FILTERS',
    'JINJA2_GENERATE_FILTERS',
)
