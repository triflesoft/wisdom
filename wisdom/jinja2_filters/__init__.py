from .circled import discover_circled
from .circled import generate_circled
from .relative_link import discover_relative_link
from .relative_link import generate_relative_link

JINJA2_DISCOVER_FILTERS = {
    'circled': discover_circled,
    'relative_link': discover_relative_link,
}

JINJA2_GENERATE_FILTERS = {
    'circled': generate_circled,
    'relative_link': generate_relative_link,
}

__all__ = (
    'JINJA2_DISCOVER_FILTERS',
    'JINJA2_GENERATE_FILTERS',
)
