from .base import embed_extension


class AsideGenerateExtension(embed_extension('AsideGenerateExtensionBase', 'aside')):
    def _process_markup(self, context, source_path, source_line, caller, content_path=None):
        content_text = None

        if content_path:
            with open(content_path, 'r', newline='') as content_file:
                content_text = content_file.read()
        else:
            content_text = str(caller())

        return f'''
<aside>
<div class="header-placeholder">&nbsp;</div>
<div class="aside-content">{content_text}</div>
</aside>'''
