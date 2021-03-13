from jinja2 import contextfilter
from os.path import dirname
from os.path import relpath


def discover_relative_link(path):
    return path


@contextfilter
def generate_relative_link(context, resource_link):
    template_output_link = context['this'].output_link
    relative_link = relpath(resource_link, dirname(template_output_link))

    return '' if relative_link == '.' else relative_link
