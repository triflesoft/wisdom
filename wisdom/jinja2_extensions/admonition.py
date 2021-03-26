from .base import discover_extension
from .base import generate_extension


AdmonitionDiscoverExtension = discover_extension('AdmonitionDiscoverExtension', 'admonition')


class AdmonitionGenerateExtension(generate_extension('AdmonitionGenerateExtensionBase', 'admonition', ['note'])):
    def _process_markup(self, context, kind, caller):
        this_output_link = context['this'].output_link
        icon_link = f'static/images/icon-admonition-{kind}.svg'
        text = str(caller())

        return f'''
<div class="admonition-outer admonition-outer-{kind}">
    <div class="admonition-inner admonition-inner-{kind}">
        <figure class="admonition admonition-{kind}">
            <img class="admonition admonition-{kind}" src="{icon_link}" />
        </figure>
        <p class="admonition admonition-{kind}">{text}</p>
    </div>
</div>'''
