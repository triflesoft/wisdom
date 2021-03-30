from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
from re import compile
from urllib.parse import quote

from .base import discover_content_extension
from .base import generate_content_extension


CIRCLED_TEXT = compile('[\u2776\u2777\u2778\u2779\u277A\u277B\u277C\u277D\u277E\u277F]')
CIRCLED_HTML = compile('<span style="[^"]+">([\u2776\u2777\u2778\u2779\u277A\u277B\u277C\u277D\u277E\u277F])</span>')


PygmentsDiscoverExtension = discover_content_extension('PygmentsDiscoverExtension', 'pygments')


class PygmentsGenerateExtension(generate_content_extension('PygmentsGenerateExtensionBase', 'pygments')):
    def _process_markup(self, context, caller, lexer=None, style=None):
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
        code_html = CIRCLED_HTML.sub('\\1', code_html)
        code_html_lines = code_html.splitlines()
        code_html = '</li><li>'.join(code_html_lines)
        code_text = CIRCLED_TEXT.sub('', code_text)

        return f'''
<div class="source-code-outer source-code-pygments">
    <button class="original-code-copy" data-original-code="{quote(code_text)}">
        <img class="original-code-copy" src="static/images/icon-source-code-copy.svg" alt="" />
    </button>
    <div class="source-code-inner"><ol><li>{code_html}</li></ol></div>
</div>'''
