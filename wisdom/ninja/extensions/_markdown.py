from commonmark import Parser
from commonmark import HtmlRenderer

from .base import embed_extension


class MarkDownGenerateExtension(embed_extension('MarkDownGenerateExtensionBase', 'markdown')):
    def _process_markup(self, context, source_path, source_line, caller, content_path=None):
        content_text = None

        if content_path:
            with open(content_path, 'r', newline='') as content_file:
                content_text = content_file.read()
        else:
            content_text = str(caller())

        code_ast = Parser().parse(content_text)
        code_html = HtmlRenderer().render(code_ast)

        return code_html
