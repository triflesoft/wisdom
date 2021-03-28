from .base import discover_content_extension
from .base import generate_content_extension


AdmonitionDiscoverExtension = discover_content_extension('AdmonitionDiscoverExtension', 'admonition')


class AdmonitionGenerateExtension(generate_content_extension('AdmonitionGenerateExtensionBase', 'admonition')):
    def _process_markup(self, context, caller, kind='note'):
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
