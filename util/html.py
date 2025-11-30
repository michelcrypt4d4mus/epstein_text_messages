from rich.terminal_theme import TerminalTheme

from .env import args


PAGE_TITLE = "Epstein Estate Documents - Seventh Production Collection Reformatted Text Messages"

CONSOLE_HTML_FORMAT = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/x-icon" href="https://media.universeodon.com/accounts/avatars/109/363/179/904/598/380/original/eecdc2393e75e8bf.jpg" />

    <style>
        {stylesheet}
        body {{
            color: {foreground};
            background-color: {background};
        }}
    </style>
""" + f"<title>Epstein {'Emails' if args.all else 'Text Messages'}</title>" + """
</head>
<body>
    <pre style="font-family: Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace; white-space: pre-wrap; overflow-wrap: break-word;">
        <code style="font-family: inherit; white-space: pre-wrap; overflow-wrap: break-word;">
            {code}
        </code>
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
