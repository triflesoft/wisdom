from .base import discover_extension
from .base import generate_extension

from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name


PygmentsDiscoverExtension = discover_extension('PygmentsDiscoverExtension', 'pygments')


class PygmentsGenerateExtension(generate_extension('PygmentsGenerateExtensionBase', 'pygments', [None, None])):
    def _process_markup(self, context, lexer, style, caller):
        code_text = str(caller())
        code_lexer = lexer or context['component'].variables.get('pygments_lexer', None)
        code_style = style or context['component'].variables.get('pygments_style', 'default')

        if code_lexer is None:
            code_lexer = guess_lexer(code_text, stripall=True, ensurenl=True)
        else:
            code_lexer = get_lexer_by_name(code_lexer, stripall=True, ensurenl=True)

        code_style = get_style_by_name(code_style)
        code_formatter = HtmlFormatter(style=code_style, nowrap=True, noclasses=True)
        code_html = highlight(code_text, code_lexer, code_formatter)
        code_html_lines = code_html.splitlines()
        code_html = '</li><li>'.join(code_html_lines)

        return f'<code class="pygments"><button class="copy"></button><pre><ol><li>{code_html}</li></ol></pre></code>'
