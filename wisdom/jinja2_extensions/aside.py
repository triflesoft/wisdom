from .base import content_extension


class AsideGenerateExtension(content_extension('AsideGenerateExtensionBase', 'aside')):
    def _process_markup(self, context, caller):
        content_text = str(caller())

        return f'''
<aside>
<div class="header-placeholder">&nbsp;</div>
<div class="aside-content">{content_text}</div>
</aside>'''
