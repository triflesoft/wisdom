from jinja2 import contextfilter
from jinja2 import escape
from jinja2 import Markup
from logging import error
from os.path import join
from os.path import normpath
from unicodedata import normalize


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


def h1(text):
    return Markup(f'<h1 id="h1_{id_from_text(text)}">{escape(text)}</h1>')


def h2(text):
    return Markup(f'<h2 id="h2_{id_from_text(text)}">{escape(text)}</h2>')


def h3(text):
    return Markup(f'<h3 id="h3_{id_from_text(text)}">{escape(text)}</h3>')


def h4(text):
    return Markup(f'<h4 id="h4_{id_from_text(text)}">{escape(text)}</h4>')


def h5(text):
    return Markup(f'<h5 id="h5_{id_from_text(text)}">{escape(text)}</h5>')


def h6(text):
    return Markup(f'<h6 id="h6_{id_from_text(text)}">{escape(text)}</h6>')


def discover_a_page(path):
    return Markup(f'<a href="{path}">{path}</a>')


@contextfilter
def generate_a_page(context, path):
    this = context['this']
    templates = context['templates']

    if ':' in path:
        component_code, template_family = path.split(':', 1)
    else:
        component_code, template_family = this.component.code, path

    if template_family.startswith('..'):
        template_family = normpath(join(this.family, template_family))

    for template in templates:
        if (template.component.code == component_code) and (template.family == template_family):
            title = template.variables['title']
            parent = template.parent

            while parent:
                title = f'{parent.variables["title"]} / {title}'
                parent = parent.parent

            return Markup(f'<a class="nav-internal" href="{template.output_link}">{escape(title)}</a>')

    error('Path "%s" cannot be resolved into template.', path)
    raise RuntimeError()


