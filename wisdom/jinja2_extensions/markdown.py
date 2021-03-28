from .base import discover_content_extension
from .base import generate_content_extension

from commonmark import Parser
from commonmark import HtmlRenderer

MarkDownDiscoverExtension = discover_content_extension('MarkDownDiscoverExtension', 'markdown')


class MarkDownGenerateExtension(generate_content_extension('MarkDownGenerateExtensionBase', 'markdown')):
    def _process_markup(self, context, caller):
        code_text = str(caller())
        code_ast = Parser().parse(code_text)
        code_html = HtmlRenderer().render(code_ast)

        return code_html
