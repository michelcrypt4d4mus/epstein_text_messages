"""
slightly more abstract / higher level functions for turning rich objs to HTML
"""
from copy import deepcopy
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from rich.align import Align
from rich.panel import Panel
from rich.console import RenderableType
from rich.padding import Padding
from rich.style import Style
from rich.table import Table
from rich.text import Text

from epstein_files.output.html.elements import _html_elements_to_str
from epstein_files.output.html.elements import *
from epstein_files.output.html.positioned_rich import *
from epstein_files.output.html.rich_style import RichStyle
from epstein_files.output.rich import console
from epstein_files.util.constant.html import CUSTOM_HTML_TEMPLATE, HTML_TERMINAL_THEME
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import add_constant, listify, update_truthy
from epstein_files.util.helpers.file_helper import log_file_write
from epstein_files.util.helpers.string_helper import join_truthy
from epstein_files.util.logging import logger

CSS = Path(__file__).parent.joinpath('page.css').read_text()
DEFAULT_HTML_TABLE_BORDER_STYLE = 'dim grey11'
BOX_BORDER_RADIUS = 4
BOX_BORDER_WIDTH = 2
MAX_RENDER_WIDTH = 1024
VERTICAL_MARGIN_EMS = to_em(VERTICAL_MARGIN)
BOTTOM_MARGIN_PROPS = {'margin-bottom': VERTICAL_MARGIN_EMS}

# Makes the inset border work
OUTER_PANEL_DIV_PADDING_CSS = dimensions_to_padding_css(
    (
        BORDER_VERTICAL_PADDING,
        BORDER_VERTICAL_PADDING,
    )
)

DEFAULT_HTML_RENDERER_KWARGS = {
    'code_format': PRE_CONSOLE_TEMPLATE,
    'inline_styles': True,
    'theme': HTML_TERMINAL_THEME,
}

# These are the props for the outer panel
PANEL_BASE_PROPS = {
    "display": "inline-block",
    'width': 'fit-content',
    **OUTER_PANEL_DIV_PADDING_CSS,
}

PANEL_BORDER_PROPS = {
    "border-radius": to_px(BOX_BORDER_RADIUS),
    "border-style": "solid",
    "border-width": to_px(BOX_BORDER_WIDTH),
}


# TODO: refactor this into RichStyle
def border_css_props(style: str | Style | None) -> dict[str, str]:
    """CSS props to make an HTML div with border-color set to `style` arg as a standard CSS RGB string."""

    if style and (html_style := RichStyle(style)).foreground_color_hex:
        return {
            "border-color": html_style.foreground_color_hex,
            **PANEL_BORDER_PROPS
        }
    else:
        return {}


def console_buffer_to_html(_console: Console, clear: bool = True) -> str:
    """
    Export the current `console` write buffer to an HTML string.
    SPLITTER is used to strip off cruft that rich export_html() creates because it prints to variables we don't want.
    """
    return _console.export_html(clear=clear, **DEFAULT_HTML_RENDERER_KWARGS).split(SPLITTER)[0]


def one_row_table_html(table: Table, css_props: OptionalCssProps = None) -> str:
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
            'border-bottom-color': RichStyle(table.border_style).foreground_color_hex,
            'text-align': header.justify or 'left',
            **(RichStyle(table.header_style).to_css if table.header_style else {}),
        }

        header_span = render_to_html(Text('', style=col1.header_style or '').append(header))
        header_div = div_class(header_span, 'document_panel_header', header_props)

    body_html = render_to_html(Text('', style=col1.style).append(col1._cells[0]))
    body_div = div_class(body_html, PANEL_BODY_CSS_CLASS, PANEL_BASE_PROPS)

    return div_class(
        join_truthy(header_div, body_div, '\n'),
        BLACK_BG__NO_EXPAND,
        {
            'text-align': col1.justify,
            **border_css_props(table.border_style),
            **css_props
        }
    )


def panel_to_div(panel: Panel, css_props: OptionalCssProps) -> str:
    """
    Convert a rich `Panel` to a div that looks the same.
    this requires two divs with padding between them to approximate the inset border of rich ansi
    css_props are applied to the OUTER div.
    """
    css_props = css_props if css_props is not None else BOTTOM_MARGIN_PROPS                            # TODO: Default bottom margin seems wrong
    border_style = panel.border_style if panel.style == 'none' or not panel.style else panel.style     # TODO: what's up with the string 'none'??
    inner_div_padding_dims = add_constant(unpack_dimensions(panel.padding or 0), MAKEUP_PADDING)
    html_style = RichStyle(panel.style)

    inner_div_css = {
        **html_style.to_css,
        **border_css_props(border_style),
        **dimensions_to_padding_css(inner_div_padding_dims),
    }

    outer_div_css = {
        **html_style.to_css,
        **PANEL_BASE_PROPS,
        **css_props,
    }

    # Set the width but only on the inner div. outer div will adjust automatically based on its padding
    if panel.width:
        for prop in WIDTH_PROPS:
            inner_div_css[prop] = to_em(panel.width - MAKEUP_PADDING)

    logger.debug(f"panel_to_div(): panel.style='{panel.style}', panel.border_style='{panel.border_style}'\n\n   inner_div_css props: {inner_div_css}\n\n    outer_div_css: {outer_div_css}\n")
    inner_div = div_class(render_at_css_width(panel.renderable), 'panel inner_panel', inner_div_css)
    return div_class(inner_div, 'panel outer_panel', outer_div_css)


def render_at_console_width(obj: RenderableType) -> str:
    """render at the width currently used by the main rich.Console obj."""
    return _render_at_width(obj, console.width)


def render_at_css_width(obj: RenderableType, props: OptionalCssProps = None) -> str:
    """Convert CssProps to rich Padding units."""
    props = props or {}
    css_width = from_em(props.get('max-width', props.get('width')))

    if css_width:
        logger.debug(f"render_at_css_width() extracted width of {css_width} from `props` arg CSS:\n   {props}\n")
    else:
        logger.debug(f"no width found in CSS when render_at_css_width() called, no point in using this function.")

    return _render_at_width(obj, css_width or HTML_RENDER_CONSOLE.width)


def render_at_obj_width(obj: RenderableType) -> str:
    """Render `obj` to a <pre> block with same width as `obj`."""
    with _obj_width_renderer(obj) as _renderer:
        return render_to_html(obj, _renderer)


def render_max_width(obj: RenderableType) -> str:
    """render obj to a <pre> block formatted entirely by rich monospace layout that is MAX_RENDER_WIDTH chars wide."""
    return _render_at_width(obj, MAX_RENDER_WIDTH)


def render_to_html(obj: RenderableType, renderer_console: Console | None = None) -> str:
    """Convert rich renderable to HTML <pre> str by printing it then calling `console.export_html()`."""
    renderer_console = renderer_console or HTML_RENDER_CONSOLE
    renderer_console.print(obj, end='')
    return console_buffer_to_html(renderer_console)


def table_to_html(table: Table, css_props: OptionalCssProps = None) -> str:
    """Convert a rich `Table` to an HTML table that looks the same."""
    css_props = css_props or {}
    col_styles = [col.style or '' for col in table.columns]
    border_style = RichStyle(table.border_style or DEFAULT_HTML_TABLE_BORDER_STYLE)
    border_color_css = {'border-color': border_style.foreground_color_hex, 'border-style': 'solid'}
    header_css_props = RichStyle(table.header_style).to_css if table.header_style else {}

    # TODO: seems like we could just use border_color_css?
    if not table.show_lines:
        header_css_props['border-bottom-color'] = border_style.foreground_color_hex
        header_css_props['border-bottom-width'] = to_px(1)
        header_css_props['border-bottom-style'] = 'solid'

    row_props = {'border-bottom-width': '1px', **border_color_css} if table.show_lines else {}

    cell_props = {
        **row_props,
        **(padding_vertical_css(MAKEUP_PADDING) if table.show_lines and '_no_pad' not in dir(table) else {})  # TODO: hacky af
    }

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

    # table.caption is the text at the bottom under the table, the footer kinda
    if table.caption:
        caption = table.caption if isinstance(table.caption, Text) else Text(table.caption)
        caption_style = RichStyle(table.caption_style or '')

        caption_html = text_to_div(
            caption,
            {
                'margin-top': to_em(0.4),  # TODO: make this config
                'text-align': 'center',
                'width': '90%',
                **css_props,
                **caption_style.to_css,
                **CENTERED
            }
        )
    else:
        caption_html = ''

    rows = [headers, *rows] if table.show_header else rows
    html_rows = [div_class('\n'.join(row), 'row', row_props, role='row') for row in rows]

    # Do positioning and layout
    table_html = div_class(
        html_rows,
        'table',
        border_css_props(table.border_style),
        role='table'
    )

    return div_class(
        _html_elements_to_str([_table_title_html(table), table_html, caption_html]),
        'table_container',
        {**BOTTOM_MARGIN_PROPS, **css_props},
    )


def text_to_div(txt: Text, css_props: OptionalCssProps, class_name: str = BLACK_BG__NO_EXPAND) -> str:
    """Wrap a line or block of text in a plain black background div."""
    if css_props:
        logger.debug(f"text_to_div() called with css_props arg:\n  {css_props}\n")

    return div_class(render_at_css_width(txt), class_name, css_props)


def text_to_list(textish: list[str] | list[Text], list_type: HtmlListTag = 'ul', **kwargs) -> str:
    """Convert a list of strings or a string with newlines in it to HTML list (<ul> or <ol> tag)."""
    txts = [Text(t) if isinstance(t, str) else t for t in textish]
    html_elements = [strip_outer_tag(render_max_width(txt), 'pre') for txt in txts]
    return build_html_list(html_elements, list_type, **kwargs)


@contextmanager
def tmp_console(tmp_width: int) -> Generator[Console, None, None]:
    """safely use a rich console with temporary width for rendering rich -> HTML."""
    old_console_width = HTML_RENDER_CONSOLE.width
    HTML_RENDER_CONSOLE.width = tmp_width

    try:
        yield HTML_RENDER_CONSOLE
    finally:
        HTML_RENDER_CONSOLE.width = old_console_width


def write_templated_html(elements: list[str] | str, output_path: Path) -> Path:
    """Render a collection of HTML elements to an HTML file. Returns file that was written."""
    html = str(CUSTOM_HTML_TEMPLATE).format(
        code='\n\n'.join(listify(elements)),
        stylesheet=CSS,
        background=HTML_TERMINAL_THEME.background_color.hex,
        foreground=HTML_TERMINAL_THEME.foreground_color.hex,
    )

    output_path.write_text(html)
    log_file_write(output_path)
    return output_path


@contextmanager
def _obj_width_renderer(obj: RenderableType) -> Generator[Console, None, None]:
    """temporarily set html_renderer.width to this object's width to constrain rich output."""
    with tmp_console(HTML_RENDER_CONSOLE.measure(obj).minimum) as _tmp_console:
        yield _tmp_console


def _render_at_width(obj: RenderableType, width: int) -> str:
    """render `obj` to HTML but temporarily change the console width."""
    with tmp_console(width) as _renderer:
        return render_to_html(obj, _renderer)


def _table_cell(contents: RenderableType, props: OptionalCssProps = None, extra_class: str = '') -> str:
    cell_html = render_at_css_width(contents, props)
    return div_class(cell_html, join_truthy(extra_class, 'column'), props, role='cell')


def _table_title_html(table: Table) -> str:
    """Create HTML to render a table's title (line above the border)."""
    if table.title is None or len(table.title) == 0:
        return ''

    title_txt = table.title.copy() if isinstance(table.title, Text) else Text(table.title)

    if table.title_style:
        title_txt.stylize(table.title_style)

    title_justify = 'center' if table.title_justify in ['default', 'full'] else table.title_justify
    title_css = alignment_css(title_justify)

    if title_justify == 'center':
        title_css['text-align'] = 'center'

    return div_class(render_to_html(title_txt), 'table_title', title_css)
