from .base import discover_extension
from .base import generate_extension

from commonmark import Parser
from commonmark import HtmlRenderer

MarkDownDiscoverExtension = discover_extension('MarkDownDiscoverExtension', 'markdown')


class MarkDownGenerateExtension(generate_extension('MarkDownGenerateExtensionBase', 'markdown', [])):
    def _process_markup(self, context, caller):
        code_text = str(caller())
        code_ast = Parser().parse(code_text)
        code_html = HtmlRenderer().render(code_ast)

        return f'<code class="pygments"><pre>{code_html}</pre></code>'
