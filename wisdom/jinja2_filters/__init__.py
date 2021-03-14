from .circled import discover_circled
from .circled import generate_circled
from .relative_link import discover_relative_link
from .relative_link import generate_relative_link
from .subresource_integrity import discover_subresource_integrity
from .subresource_integrity import generate_subresource_integrity

JINJA2_DISCOVER_FILTERS = {
    'circled': discover_circled,
    'relative_link': discover_relative_link,
    'subresource_integrity': discover_subresource_integrity,
}

JINJA2_GENERATE_FILTERS = {
    'circled': generate_circled,
    'relative_link': generate_relative_link,
    'subresource_integrity': generate_subresource_integrity,
}

__all__ = (
    'JINJA2_DISCOVER_FILTERS',
    'JINJA2_GENERATE_FILTERS',
)
