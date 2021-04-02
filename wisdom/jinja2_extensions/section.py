from jinja2 import escape
from jinja2 import TemplateSyntaxError
from logging import error
from unicodedata import normalize

from .base import content_extension


TRANSLITERATE_MAP = {
    '-': '-',
    '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
    'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j',
    'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 'q': 'q', 'r': 'r', 's': 's', 't': 't',
    'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z',
    'а': 'a',  'б': 'b',  'в': 'v',  'г': 'g',  'д': 'd',  'е': 'e',  'ж': 'zh', 'з': 'z', 'и': 'i',  'к': 'k',
    'л': 'l',  'м': 'm',  'н': 'n',  'о': 'o',  'п': 'p',  'р': 'r',  'с': 's',  'т': 't', 'у': 'u',  'ф': 'f',
    'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sh', 'ъ': 'q',  'ы': 'y',  'ь': 'w', 'э': 'ye', 'ю': 'yu',
    'я': 'ya',
    'ა': 'a',  'ბ': 'b',  'გ': 'g',  'დ': 'd',  'ე': 'e',  'ვ': 'v',  'ზ': 'z',  'თ': 't',  'ი': 'i',  'კ': 'k',
    'ლ': 'l',  'მ': 'm',  'ნ': 'n',  'ო': 'o',  'პ': 'p',  'ჟ': 'zh', 'რ': 'r',  'ს': 's',  'ტ': 't',  'უ': 'u',
    'ფ': 'f',  'ქ': 'k',  'ღ': 'gh', 'ყ': 'q',  'შ': 'sh', 'ჩ': 'ch', 'ც': 'ts', 'ძ': 'dz', 'წ': 'ts', 'ჭ': 'ch',
    'ხ': 'kh', 'ჯ': 'j',  'ჰ': 'h',
}


def id_from_text(text):
    text = normalize('NFD', text.lower())

    return ''.join(TRANSLITERATE_MAP.get(c, '_') for c in text)


class SectionGenerateExtension(content_extension('SectionGenerateExtensionBase', 'section')):
    def _process_markup(self, context, caller, h2=None, h3=None, h4=None, h5=None, h6=None):
        content_text = str(caller())

        header_text = ''
        header_type = ''

        if h6:
            header_text = h6
            header_type = 'h6'
        elif h5:
            header_text = h5
            header_type = 'h5'
        elif h4:
            header_text = h4
            header_type = 'h4'
        elif h3:
            header_text = h3
            header_type = 'h3'
        elif h2:
            header_text = h2
            header_type = 'h2'
        else:
            error(
                'Document "%s:%d" contains invalid section. Either h2, h3, h4, h5, or h6 must be specified.',
                self.source_path,
                self.source_line)

            raise RuntimeError()

        return f'''
<section data-level="{header_type}">
<{header_type} id="{header_type}_{id_from_text(header_text)}">{escape(header_text)}</{header_type}>
<div class="section-content">
{content_text}
</div>
</section>'''
