from .base import embed_extension


class AdmonitionGenerateExtension(embed_extension('AdmonitionGenerateExtensionBase', 'admonition')):
    def _process_markup(self, context, source_path, source_line, caller, content_path=None, kind='note'):
        icon_link = f'static/images/icon-admonition-{kind}.svg'
        content_text = None

        if content_path:
            with open(content_path, 'r', newline='') as content_file:
                content_text = content_file.read()
        else:
            content_text = str(caller())

        return f'''
<div class="admonition-outer admonition-outer-{kind}">
    <div class="admonition-inner admonition-inner-{kind}">
        <figure class="admonition admonition-{kind}">
            <img class="admonition admonition-{kind}" src="{icon_link}" alt="{kind}"/>
        </figure>
        <p class="admonition admonition-{kind}">{content_text}</p>
    </div>
</div>'''
