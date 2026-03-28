from dataclasses import dataclass
from rich.terminal_theme import TerminalTheme

from epstein_files.output.site.sites import Site
from epstein_files.util.env import args
from epstein_files.util.helpers.string_helper import indented

PAGE_TITLE = '   ∞ Michel de Cryptadamus ∞   '
FONT_FAMILY = "Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"

STYLE_TEMPLATE = """{stylesheet}
body {{
    background-color: {background};
    color: {foreground};
}}"""

GOOGLE_FONTS_LINKS = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Gloria+Hallelujah&family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&family=Special+Elite&display=swap" rel="stylesheet">
"""

@dataclass
class HtmlTemplate:
    body: str

    def __str__(self) -> str:
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Epstein {self.page_type()}</title>
    <link rel="icon" type="image/x-icon" href="https://media.universeodon.com/accounts/avatars/109/363/179/904/598/380/original/eecdc2393e75e8bf.jpg" />
    <meta charset="UTF-8">
    {self.js_redirect()}
    {GOOGLE_FONTS_LINKS}

    <style>
        {STYLE_TEMPLATE}
    </style>
</head>

<body>
    {self.body}
</body>
</html>"""

    def js_redirect(self) -> str:
        if args.mobile or args.names:
            return ''
        else:
            return """
    <script type="text/javascript">
        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {{
            window.location.href = """ + f'"{Site.get_mobile_redirect_url(args._site)}";' + """
        }}
    </script>"""

    def page_type(self) -> str:
        # TODO: this should be integrated with sites config
        if args.all_emails:
            return 'Emails'
        elif args.all_emails_chrono:
            return 'Chronological Emails'
        else:
            return 'Curated'


CUSTOM_HTML_TEMPLATE = HtmlTemplate(
    """<div class="doc_container page_container">\n        {code}\n    </div>"""
)

RICH_HTML_TEMPLATE = HtmlTemplate(
    f"""<pre style="font-family:{FONT_FAMILY}"><code style="font-family:inherit">{{code}}</code></pre>""",
)


# Swap black for white
HTML_TERMINAL_THEME = TerminalTheme(
    (0, 0, 0),
    (255, 255, 255),
    [
        (0, 0, 0),
        (128, 0, 0),
        (0, 128, 0),
        (128, 128, 0),
        (0, 0, 128),
        (128, 0, 128),
        (0, 128, 128),
        (192, 192, 192),
    ],
    [
        (128, 128, 128),
        (255, 0, 0),
        (0, 255, 0),
        (255, 255, 0),
        (0, 0, 255),
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 255),
    ],
)
