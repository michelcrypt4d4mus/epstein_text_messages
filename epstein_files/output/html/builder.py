from copy import deepcopy
from os import devnull
from pathlib import Path
from typing import Mapping

from rich.console import Console, RenderableType
from rich.style import Style
from rich.table import Table
from rich.text import Text

from epstein_files.output.html.elements import *
from epstein_files.output.rich import CONSOLE_KWARGS as DEFAULT_CONSOLE_KWARGS
from epstein_files.util.constant.html import HTML_TERMINAL_THEME
from epstein_files.util.helpers.file_helper import log_file_write
from epstein_files.util.logging import logger

SPLITTER = '-# JUNK #-'
SPLITTER_TEMPLATE = SPLITTER + """{stylesheet} {background} {foreground}"""  # these template vars allow export_html() to work
PRE_TEMPLATE = pre_console_template() + SPLITTER_TEMPLATE
PRE_CODE_TEMPLATE = pre_code_console_template() + SPLITTER_TEMPLATE

BOX_BORDER_RADIUS = 4
BOX_BORDER_WIDTH = 1
BOX_HORIZONTAL_PADDING = '1em'
BOX_VERTICAL_PADDING = 7

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <style>
        .container {{
            display: flex;
            flex-direction: column;
        }}

        body {{
            background-color: {background};
            color: {foreground};
        }}

        pre {{
            margin-top: 0px;
            margin-bottom: 0px;
        }}
    </style>
</head>

<body>
    <div class="container">
        {body}
    </div>
</body>
</html>
"""

PANEL_BASE_PROPS = {
    "border-radius": to_px(BOX_BORDER_RADIUS),
    "display": "inline-block",
    'width': 'fit-content',
    **padding_props(BOX_HORIZONTAL_PADDING, BOX_VERTICAL_PADDING)
}

PANEL_BORDER_PROPS = {
    "border-style": "solid",
    "border-width": to_px(BOX_BORDER_WIDTH),
}


def border_css_props(style: str | Style) -> dict[str, str]:
    style = style if isinstance(style, Style) else Style.parse(style)

    if style and style.color:
        return {
            "border-color": style.color.get_truecolor(HTML_TERMINAL_THEME).hex,
            **PANEL_BORDER_PROPS
        }
    else:
        return {}


def in_padded_div(txt: Text) -> str:
    return div_tag(rich_to_html(txt), PANEL_BASE_PROPS)


def rich_to_html(obj: RenderableType) -> str:
    html_console.print(obj, end='')
    html_text = html_console.export_html(theme=HTML_TERMINAL_THEME, code_format=PRE_TEMPLATE, inline_styles=True)
    return html_text.split(SPLITTER)[0]  # Strip cruft we need to have templated to get export_html() to work


# def table_to_html(table: Table) -> str:
#     rows = [
#         [table.columns[j]._cells[i] for j in range(0, len(table.columns))]
#         for i, row in enumerate(table.rows)
#     ]




#         table.add_row(
#             # Collapse all but last col into one
#             Group(
#                 *[_table.columns[j]._cells[i] for j in range(1, max_col_idx)],
#                 _table.columns[0]._cells[i],
#             ),
#             _table.columns[max_col_idx]._cells[i],
#             style=row.style
#         )



def write_html(divs: list[str], output_path: Path = Path.cwd().joinpath('html_test.html')) -> Path:
    body = '\n\n'.join(divs)

    html = HTML_TEMPLATE.format(
        body=body,
        background=HTML_TERMINAL_THEME.background_color.hex,
        foreground=HTML_TERMINAL_THEME.foreground_color.hex,
    )

    output_path.write_text(html)
    log_file_write(output_path)
    return output_path
