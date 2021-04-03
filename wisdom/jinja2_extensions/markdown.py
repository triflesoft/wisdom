from commonmark import Parser
from commonmark import HtmlRenderer

from .base import content_extension


class MarkDownDiscoverExtension(content_extension('MarkDownDiscoverExtensionnBase', 'markdown')):
    def _process_markup(self, context, source_path, source_line, caller):
        code_text = str(caller())
        code_ast = Parser().parse(code_text)
        code_html = HtmlRenderer().render(code_ast)

        return code_html


class MarkDownGenerateExtension(content_extension('MarkDownGenerateExtensionBase', 'markdown')):
    def _process_markup(self, context, source_path, source_line, caller):
        code_text = str(caller())
        code_ast = Parser().parse(code_text)
        code_html = HtmlRenderer().render(code_ast)

        return code_html
