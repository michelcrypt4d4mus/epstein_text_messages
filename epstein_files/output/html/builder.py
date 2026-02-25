from copy import deepcopy
from pathlib import Path
from typing import Mapping

from rich.console import RenderableType
from rich.style import Style
from rich.table import Table
from rich.text import Text

from epstein_files.output.html.elements import *
from epstein_files.util.constant.html import CUSTOM_HTML_TEMPLATE, HTML_TERMINAL_THEME
from epstein_files.util.helpers.data_helpers import listify
from epstein_files.util.helpers.file_helper import log_file_write
from epstein_files.util.helpers.string_helper import join_truthy
from epstein_files.util.logging import logger

CSS = Path(__file__).parent.joinpath('page.css').read_text()
BOX_BORDER_RADIUS = 4
BOX_BORDER_WIDTH = 1
BORDER_HORIZONTAL_PADDING = to_em(1)
BORDER_VERTICAL_PADDING = to_em(0.5)
VERTICAL_MARGIN = to_em(1.5)  # Between elements
BOTTOM_MARGIN_PROPS = {'margin-bottom': VERTICAL_MARGIN}
VERTICAL_MARGIN_PROPS = vertical_margin_props(VERTICAL_MARGIN)

PANEL_BASE_PROPS = {
    "display": "inline-block",
    'width': 'fit-content',
    **padding_props(BORDER_HORIZONTAL_PADDING, BORDER_VERTICAL_PADDING)
}

PANEL_BORDER_PROPS = {
    "border-radius": to_px(BOX_BORDER_RADIUS),
    "border-style": "solid",
    "border-width": to_px(BOX_BORDER_WIDTH),
}


def body_panel_css_props(border_style: str | Style | None) -> dict[str, str]:
    """CSS for panel with Document text."""
    return {
        **border_css_props(border_style),
        **PANEL_BASE_PROPS,
    }


def border_css_props(style: str | Style | None) -> dict[str, str]:
    if style is None:
        return {}

    html_style = HtmlStyle(style)

    if html_style.hex:
        return {
            "border-color": html_style.hex,
            **PANEL_BORDER_PROPS
        }
    else:
        return {}


def buffer_as_html(_console: Console, clear: bool = True) -> str:
    html = _console.export_html(
        clear=clear,
        code_format=PRE_CONSOLE_TEMPLATE,
        inline_styles=True,
        theme=HTML_TERMINAL_THEME,
    )

    return html.split(SPLITTER)[0]  # Strip cruft we need to have templated to get export_html() to work


def rich_to_html(
    obj: RenderableType,
    props: CssProps = None,
    minimize_width: bool = False,
    maximize_width: bool = False
) -> str:
    """Convert a rich renderable to HTML string."""
    props = props or {}
    old_console_width = html_console.width
    html_console.width = from_em(props.get('max-width') or props.get('width')) or html_console.width

    if minimize_width:
        measurement = html_console.measure(obj)
        logger.debug(f"renderable has measurement: {measurement}")
        html_console.width = measurement.minimum
    elif maximize_width:
        html_console.width = 1024

    if html_console.width != old_console_width:
        logger.debug(f"Temporarily set console width to {html_console.width}")

    html_console.print(obj, end='')
    html_text = buffer_as_html(html_console)
    html_console.width = old_console_width
    return html_text


def table_to_html(table: Table, with_horizontal_lines: bool = False, css_props: CssProps = None) -> str:
    col_styles = [col.style or '' for col in table.columns]
    border_props = border_css_props(table.border_style)
    header_css_props = HtmlStyle(table.header_style).to_css if table.header_style else {}
    row_props = {'border-bottom': '1px solid dimgray'} if with_horizontal_lines else {}

    if table.title:
        title_txt = table.title.copy() if isinstance(table.title, Text) else Text(table.title)

        if table.title_style:
            title_txt.stylize(table.title_style)

        title_html = rich_to_html(title_txt)
    else:
        title_html = ''

    cell_props = {
        **row_props,
        **(vertical_pad_props(to_em(0.5)) if with_horizontal_lines else {})
    }

    headers = [
        table_cell(
            Text('', style=col.header_style or '').append(col.header),
            {
                'max-width': to_em(col.max_width or col.width),
                'text-align': ((col.header.justify or '') if isinstance(col.header, Text) else '') or col.justify,
                **header_css_props
            },
            'columnheader'
        )
        for col in table.columns
    ]

    rows = [
        [
            table_cell(
                Text('', style=col_styles[j]).append(col._cells[i]) if isinstance(col._cells[i], (str, Text)) else col._cells[i],
                {
                    'max-width': to_em(col.max_width or col.width),
                    'text-align': table.columns[j].justify,
                    **cell_props
                }
            )
            for j, col in enumerate(table.columns)
        ]
        for i, _row in enumerate(table.rows)
    ]

    if table.show_header:
        rows_with_header = [headers, *rows]

    html_rows = [div_class('\n'.join(row), 'row', row_props, role='row') for row in rows_with_header]
    table_html = div_class('\n\n'.join(html_rows), 'table', border_props, role='table')
    div_props = {**BOTTOM_MARGIN_PROPS, **(css_props or {})}
    return div_class(title_html + '\n' + table_html, 'table_container', div_props)


def table_cell(contents: RenderableType, props: CssProps = None, extra_class: str = '') -> str:
    cell_html = rich_to_html(contents, props)
    return div_class(cell_html, join_truthy(extra_class, 'column'), props, role='cell')


def text_to_div(txt: Text, css_props: dict[str, str]) -> str:
    return div_tag(rich_to_html(txt), css_props)


def one_row_table_html(table: Table, css_props: CssProps = None) -> str:
    """For printing one row/one column tables currently generated by Email objs with description."""
    border_props = border_css_props(table.border_style)
    col = table.columns[0]

    if table.show_header:
        header_props = HtmlStyle(table.header_style).to_css if table.header_style else {}

        header_div = div_class(
            rich_to_html(Text('', style=col.header_style or '').append(col.header)),
            'document_panel_header',
            {'text-align': col.header.justify, **{**header_props, **border_props}}
        )
    else:
        header_div = ''

    body_div = div_class(
        rich_to_html(Text('', style=col.style).append(col._cells[0])),
        'no_expand document_body_container',
        PANEL_BASE_PROPS
    )

    return div_class(
        header_div + '\n' + body_div,
        'no_expand',
        {
            'text-align': table.columns[0].justify,
            **border_props,
            **(css_props or {})
        }
    )


def text_to_list(elements: list[str] | list[Text], tag: str = 'ul', **kwargs) -> str:
    if elements and isinstance(elements[0], Text):
        elements = [rich_to_html(txt, maximize_width=True) for txt in elements]
        elements = [strip_outer_tag(t, 'pre') for t in elements]

    return list_tag(elements, **kwargs)


def write_templated_html(divs: list[str] | str, output_path: Path) -> Path:
    body = '\n\n'.join(listify(divs))

    html = str(CUSTOM_HTML_TEMPLATE).format(
        code=body,
        stylesheet=CSS,
        background=HTML_TERMINAL_THEME.background_color.hex,
        foreground=HTML_TERMINAL_THEME.foreground_color.hex,
    )

    output_path.write_text(html)
    log_file_write(output_path)
    return output_path
