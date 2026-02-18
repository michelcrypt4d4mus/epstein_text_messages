from rich.terminal_theme import TerminalTheme

from epstein_files.util.env import args
from epstein_files.output.sites import SiteType


PAGE_TITLE = '   ∞ Michel de Cryptadamus ∞   '

if args.all_emails:
    page_type = 'Emails'
elif args.email_timeline:
    page_type = 'Chronological Emails'
else:
    page_type = 'Text Messages'


CONSOLE_HTML_FORMAT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/x-icon" href="https://media.universeodon.com/accounts/avatars/109/363/179/904/598/380/original/eecdc2393e75e8bf.jpg" />

    <script type="text/javascript">
        if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {{
            window.location.href = """ + f'"{SiteType.get_url(SiteType.MOBILE)}";' + """
        }}
    </script>

    <style>
        {stylesheet}
        body {{
            background-color: {background};
            color: {foreground};
        }}
    </style>
""" + f"<title>Epstein {page_type}</title>" + """
</head>

<body>
    <pre style="font-family: Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace; white-space: pre-wrap; overflow-wrap: break-word;">
        <code style="font-family: inherit; white-space: pre-wrap; overflow-wrap: break-word;">{code}</code>
    </pre>
</body>
</html>
"""

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
