from copy import deepcopy
from pathlib import Path
from typing import Mapping

from rich.align import Align
from rich.panel import Panel
from rich.console import RenderableType
from rich.padding import Padding
from rich.style import Style
from rich.table import Table
from rich.text import Text

from epstein_files.output.html.html_style import HtmlStyle
from epstein_files.output.html.elements import *
from epstein_files.util.constant.html import CUSTOM_HTML_TEMPLATE, HTML_TERMINAL_THEME
from epstein_files.util.helpers.data_helpers import listify, update_truthy
from epstein_files.util.helpers.file_helper import log_file_write
from epstein_files.util.helpers.string_helper import join_truthy
from epstein_files.util.logging import logger

CSS = Path(__file__).parent.joinpath('page.css').read_text()
BOX_BORDER_RADIUS = 4
BOX_BORDER_WIDTH = 2
MAKEUP_PADDING = 0.5  # Make HTML panel padding match ANSI (there's ~0.5 spaces between "a" and "|" in "a | b" in ansi)
BORDER_HORIZONTAL_PADDING = to_em(1)
BORDER_VERTICAL_PADDING = to_em(MAKEUP_PADDING)
OUTPUT_PANEL_BORDER_PADDING = padding_props(BORDER_VERTICAL_PADDING, BORDER_VERTICAL_PADDING)  # Makes the inset border work
INNER_PANEL_PADDING = padding_props(BORDER_HORIZONTAL_PADDING, BORDER_VERTICAL_PADDING)
VERTICAL_MARGIN = to_em(1.9)  # Between elements
BOTTOM_MARGIN_PROPS = {'margin-bottom': VERTICAL_MARGIN}

# These are the props for the outer panel
PANEL_BASE_PROPS = {
    "display": "inline-block",
    'width': 'fit-content',
    **OUTPUT_PANEL_BORDER_PADDING,
}

PANEL_BORDER_PROPS = {
    "border-radius": to_px(BOX_BORDER_RADIUS),
    "border-style": "solid",
    "border-width": to_px(BOX_BORDER_WIDTH),
}


# TODO: refactor this into HtmlStyle
def border_css_props(style: str | Style | None) -> dict[str, str]:
    """CSS props to make an HTML div with border-color set to `style` arg as a standard CSS RGB string."""
    # logger.warning(f"border_css_props() style='{style}'")

    if style and (html_style := HtmlStyle(style)).foreground_color_hex:
        return {
            "border-color": html_style.foreground_color_hex,
            **PANEL_BORDER_PROPS
        }
    else:
        return {}


def console_buffer_to_html(_console: Console, clear: bool = True) -> str:
    """Export the current `console` write buffer to an HTML string."""
    html = _console.export_html(
        clear=clear,
        code_format=PRE_CONSOLE_TEMPLATE,
        inline_styles=True,
        theme=HTML_TERMINAL_THEME,
    )

    return html.split(SPLITTER)[0]  # Strip cruft we need to have templated to get export_html() to work


def one_row_table_html(table: Table, css_props: CssPropsArg = None) -> str:
    """
    Convert a one row/one column `Table` to HTML string in a way that looks like a normal panel div not a table.
    These kind of `Table`s are currently rendered by `Email` objs (the `config.description` is the "header").
    """
    css_props = css_props or {}
    col1 = table.columns[0]
    header_div = ''

    if table.show_header:
        if isinstance(col1.header, Text):
            header = col1.header
        elif isinstance(col1.header, str):
            header = Text(col1.header, justify=col1.justify)
        else:
            raise ValueError(f"invalid header type {type(col1.header).__name__} {col1.header}")

        header_props = {
            'border-bottom-color': HtmlStyle(table.border_style).foreground_color_hex,
            'text-align': header.justify or 'left',
            **(HtmlStyle(table.header_style).to_css if table.header_style else {}),
        }

        header_span = rich_to_html(Text('', style=col1.header_style or '').append(header))
        header_div = div_class(header_span, 'document_panel_header', header_props)
        # logger.debug(f"one_row_table_html() header_props: {header_props}\n\nborder_props: {border_props}\n\n")

    body_div = div_class(
        rich_to_html(Text('', style=col1.style).append(col1._cells[0])),
        'no_expand document_body_container',
        PANEL_BASE_PROPS
    )

    logger.debug(f"one_row_table_html() border_style='{table.border_style}'\n\nborder_css_props: {border_css_props(table.border_style)}")

    return div_class(
        join_truthy(header_div, body_div, '\n'),
        BLACK_BG__NO_EXPAND,
        {
            'text-align': col1.justify,
            **border_css_props(table.border_style),
            **css_props
        }
    )


def panel_to_div(panel: Panel, css_props: CssPropsArg) -> str:
    """Convert a rich `Panel` to a div that looks the same."""
    css_props = css_props if css_props is not None else BOTTOM_MARGIN_PROPS  # TODO: Default bottom margin seems wrong
    # TODO: what's up with the string 'none'??
    border_style = panel.border_style if panel.style == 'none' or not panel.style else panel.style
    color_css_props = HtmlStyle(panel.style).to_css

    inner_div_css = {
        **color_css_props,
        **border_css_props(border_style),
        **padding_tuple_to_props(unpack_padding(panel.padding or (0,)), MAKEUP_PADDING),  # Panel.padding affects inner div only
    }

    outer_div_css = {
        **color_css_props,
        **PANEL_BASE_PROPS,
        **css_props,
    }

    if panel.width:
        if panel.expand:
            logger.warning(f"Panel '{panel.title}' width={panel.width} but expand=True")

        for prop in WIDTH_PROPS:
            inner_div_css[prop] = to_em(panel.width - MAKEUP_PADDING)
            outer_div_css[prop] = to_em(panel.width)

    logger.debug(f"panel_to_div():\n         panel.style: '{panel.style}'\n  panel.border_style: '{panel.border_style}'\n  local border_style: '{border_style}'\n\ninner_div_css props: {inner_div_css}\n\nouter_div_css: {outer_div_css}\n")
    inner_div = div_class(rich_to_html(panel.renderable), 'panel inner_panel', inner_div_css)
    return div_class(inner_div, 'panel outer_panel', outer_div_css)


def rich_to_html(
    obj: RenderableType,
    props: CssPropsArg = None,
    minimize_width: bool = False,
    maximize_width: bool = False,
    html_console: Console = DEFAULT_HTML_CONSOLE,
) -> str:
    """Convert a rich `RenderableType` object to an HTML string."""
    props = props or {}
    html_console.print()
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
    html_text = console_buffer_to_html(html_console)
    html_console.width = old_console_width
    return html_text


def table_to_html(table: Table, css_props: CssPropsArg = None) -> str:
    """Convert a rich `Table` to an HTML table that looks the same."""
    css_props = css_props or {}
    col_styles = [col.style or '' for col in table.columns]
    border_props = border_css_props(table.border_style)
    header_css_props = HtmlStyle(table.header_style).to_css if table.header_style else {}
    row_props = {'border-bottom': '1px solid dimgray'} if table.show_lines else {}

    if table.title:
        title_txt = table.title.copy() if isinstance(table.title, Text) else Text(table.title)

        if table.title_style:
            title_txt.stylize(table.title_style)

        title_html = rich_to_html(title_txt)
    else:
        title_html = ''

    cell_props = {**row_props, **(vertical_pad_props(to_em(0.5)) if table.show_lines else {})}

    headers = [
        _table_cell(
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
            _table_cell(
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

    if table.caption:
        caption = table.caption if isinstance(table.caption, Text) else Text(table.caption)
        caption_style = HtmlStyle(table.caption_style or '')

        caption_html = text_to_div(
            caption,
            {
                'margin-top': to_em(0.4),
                'text-align': 'center',
                'width': '90%',
                **css_props,
                **caption_style.to_css,
                **CENTERED
            }
        )  # TODO: not always centered
    else:
        caption_html = ''

    rows = [headers, *rows] if table.show_header else rows
    html_rows = [div_class('\n'.join(row), 'row', row_props, role='row') for row in rows]
    table_html = div_class('\n\n'.join(html_rows), 'table', border_props, role='table')
    combined_html = '\n'.join([title_html, table_html, caption_html])
    div_props = {**BOTTOM_MARGIN_PROPS, **(css_props)}
    return div_class(combined_html, 'table_container', div_props)


def text_to_div(txt: Text, css_props: CssPropsArg, class_name: str = BLACK_BG__NO_EXPAND) -> str:
    """Wrap a line or block of text in a plain black background div."""
    return div_class(rich_to_html(txt), class_name, css_props)


def text_to_list(elements: list[str] | list[Text], tag: HtmlListTag = 'ul', **kwargs) -> str:
    """Convert a list of strings or a string with newlines in it to HTML list (<ul> or <ol> tag)."""
    if elements and isinstance(elements[0], Text):
        elements = [rich_to_html(txt, maximize_width=True) for txt in elements]
        elements = [strip_outer_tag(t, 'pre') for t in elements]

    return list_tag(elements, tag, **kwargs)


def unwrap_rich(obj: RenderableType, css_props: CssPropsArg = None) -> tuple[RenderableType, CssPropsArg]:
    """Convert `Align` and `Padding` to CSS and extract the inner renderable."""
    css_props = css_props or {}

    if isinstance(obj, Align):
        return unwrap_rich(obj.renderable, {**css_props, **alignment_css(obj.align)})
    elif isinstance(obj, Padding):
        margin: PaddingDimensions = (obj.top, obj.right, obj.bottom, obj.left)
        return unwrap_rich(obj.renderable, {**css_props, **margin_tuple_to_props(margin)})
    else:
        return obj, css_props
    # elif isinstance(obj, Text) and obj.justify:
    #     return obj, css_props  # TODO: maybe add alignment props for Text objs with justify prop??


def write_templated_html(elements: list[str] | str, output_path: Path) -> Path:
    """Render a collection of HTML elements to an HTML file. Returns file that was written."""
    body = '\n\n'.join(listify(elements))

    html = str(CUSTOM_HTML_TEMPLATE).format(
        code=body,
        stylesheet=CSS,
        background=HTML_TERMINAL_THEME.background_color.hex,
        foreground=HTML_TERMINAL_THEME.foreground_color.hex,
    )

    output_path.write_text(html)
    log_file_write(output_path)
    return output_path


def _table_cell(contents: RenderableType, props: CssPropsArg = None, extra_class: str = '') -> str:
    cell_html = rich_to_html(contents, props)
    return div_class(cell_html, join_truthy(extra_class, 'column'), props, role='cell')
