from jinja2 import contextfilter
from os.path import join
from os.path import relpath


def discover_relative_path(path):
    return path


@contextfilter
def generate_relative_path(context, path):
    template_output_path = context['template'].output_path
    resource_output_path = join(context['output_path'], path)

    return relpath(resource_output_path, template_output_path)
