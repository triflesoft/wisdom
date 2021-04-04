from .circled import discover_circled
from .circled import generate_circled
from .subresource_integrity import discover_subresource_integrity
from .subresource_integrity import generate_subresource_integrity


JINJA2_DISCOVER_FILTERS = {
    'circled': discover_circled,
    'subresource_integrity': discover_subresource_integrity,
}


JINJA2_GENERATE_FILTERS = {
    'circled': generate_circled,
    'subresource_integrity': generate_subresource_integrity,
}


__all__ = (
    'JINJA2_DISCOVER_FILTERS',
    'JINJA2_GENERATE_FILTERS',
)
