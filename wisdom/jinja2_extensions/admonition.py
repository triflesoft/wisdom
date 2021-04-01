from .base import content_extension


class AdmonitionDiscoverExtension(content_extension('AdmonitionDiscoverExtensionBase', 'admonition')):
    def _process_markup(self, context, caller, kind='note'):
        return ''


class AdmonitionGenerateExtension(content_extension('AdmonitionGenerateExtensionBase', 'admonition')):
    def _process_markup(self, context, caller, kind='note'):
        icon_link = f'static/images/icon-admonition-{kind}.svg'
        text = str(caller())

        return f'''
<div class="admonition-outer admonition-outer-{kind}">
    <div class="admonition-inner admonition-inner-{kind}">
        <figure class="admonition admonition-{kind}">
            <img class="admonition admonition-{kind}" src="{icon_link}" alt="{kind}"/>
        </figure>
        <p class="admonition admonition-{kind}">{text}</p>
    </div>
</div>'''
