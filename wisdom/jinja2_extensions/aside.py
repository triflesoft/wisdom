from .base import content_extension


class AsideGenerateExtension(content_extension('AsideGenerateExtensionBase', 'aside')):
    def _process_markup(self, context, source_path, source_line, caller):
        content_text = str(caller())

        return f'''
<aside>
<div class="header-placeholder">&nbsp;</div>
<div class="aside-content">{content_text}</div>
</aside>'''
