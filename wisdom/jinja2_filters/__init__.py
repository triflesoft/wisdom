from .circled import discover_circled
from .circled import generate_circled
from .subresource_integrity import discover_subresource_integrity
from .subresource_integrity import generate_subresource_integrity
from .tags import h1
from .tags import h2
from .tags import h3
from .tags import h4
from .tags import h5
from .tags import h6
from .tags import discover_a_page
from .tags import generate_a_page


JINJA2_DISCOVER_FILTERS = {
    'circled': discover_circled,
    'subresource_integrity': discover_subresource_integrity,
    'h1': h1,
    'h2': h2,
    'h3': h3,
    'h4': h4,
    'h5': h5,
    'h6': h6,
    'a_page': discover_a_page,
}


JINJA2_GENERATE_FILTERS = {
    'circled': generate_circled,
    'subresource_integrity': generate_subresource_integrity,
    'h1': h1,
    'h2': h2,
    'h3': h3,
    'h4': h4,
    'h5': h5,
    'h6': h6,
    'a_page': generate_a_page,
}


__all__ = (
    'JINJA2_DISCOVER_FILTERS',
    'JINJA2_GENERATE_FILTERS',
)
