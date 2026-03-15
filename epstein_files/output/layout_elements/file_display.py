from dataclasses import dataclass, field
from typing import Literal

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from epstein_files.output.html.builder import (PANEL_BASE_PROPS, VERTICAL_MARGIN_EMS, border_css_props,
     one_row_table_html, render_to_html, text_to_list, text_to_div, margin_vertical_css)
from epstein_files.output.html.elements import div_class, div_with_legend, div_tag
from epstein_files.output.html.html_style import HtmlStyle
from epstein_files.output.html.positioned_rich import BLACK_BACKGROUND, PositionedRich, dimensions_to_margin_css
from epstein_files.util.helpers.data_helpers import only_truthy
from epstein_files.util.helpers.link_helper import join_texts

JustifyMethod = Literal['center', 'left', 'right']

BOTTOM_PADDING = 1
SUBHEADER_VERTICAL_MARGIN = 0.3

DOC_DIV_CSS_PROPS = {
    'display': 'flex',
    'flex-direction': 'column',
}


@dataclass(kw_only=True)
class BasePanel:
    border_style: str
    text: Text | list[Text]
    title: Text | None = None
    title_justify: JustifyMethod = 'right'

    @property
    def is_list(self) -> bool:
        return isinstance(self.text, list)

    def to_div(self, _margins: list[int | float] | None = None) -> str:
        """Create an HTML <div> string for this panel."""
        margins = _margins or PositionedRich.zero_dimensions()
        div_props = dimensions_to_margin_css(margins)

        # Handle MessengerLog / TextMessage list. # TODO this sucks
        if self.is_list:
            html = text_to_list(self.text, class_name='no_bullets')
            div_props.update({'word-wrap': 'break-word'})
            return div_class(html, BLACK_BACKGROUND, div_props)

        html = render_to_html(self.text)
        div_props.update(PANEL_BASE_PROPS)
        div_props.update(border_css_props(self.border_style))

        # TODO: make the title 'dim'
        title = self.title.plain if self.title else ''
        return div_with_legend(html, title, div_props)

    def __rich__(self) -> Panel:
        return Panel(
            join_texts(self.text, '\n') if self.is_list else self.text,
            border_style=self.border_style,
            expand=False,
            title=self.title,
            title_align=self.title_justify,
        )


@dataclass(kw_only=True)
class FileDisplay:
    """Allows for proper right vs. left justify of a Document display."""
    background_color: str = ''
    body_panel: BasePanel | Table
    file_info: BasePanel | None = None
    indent: int | float = 0  # TODO: this should be a property of the BasePanel
    justify: JustifyMethod | None = None
    margin_bottom: str = VERTICAL_MARGIN_EMS  # Margin below the entire agglomeration of elements, not just the body
    subheaders: list[Text] = field(default_factory=list)

    @property
    def body_margin(self) -> list[int | float]:
        """Margin for the body. Top/bottom always zero currrently."""
        padding = PositionedRich.zero_dimensions()

        # Set subtle indent
        if self.justify == 'right':
            padding[1] = self.indent
        else:
            padding[3] = self.indent

        return padding

    @property
    def body_margin_horizontal(self) -> list[int | float]:
        """Just left and right margin, vertical margins are zeroed out."""
        margin_dimensions = self.body_margin
        margin_dimensions[0] = margin_dimensions[2] = 0
        return margin_dimensions

    @property
    def horizontal_body_margin_css(self) -> dict[str, str]:
        return dimensions_to_margin_css(self.body_margin_horizontal)

    @property
    def is_table(self) -> bool:
        return isinstance(self.body_panel, Table)

    @property
    def justified_subheaders(self) -> list[Text]:
        """Set justify `Text` to get right justification of text in right aligned elements."""
        subheaders = [txt.copy() for txt in self.subheaders]

        if self.justify:
            for txt in subheaders:
                txt.justify = self.justify

        return subheaders

    @property
    def subheader_div(self) -> str:
        if not self.subheaders:
            return ''

        css_props = {
            **self.horizontal_body_margin_css,
            **margin_vertical_css(SUBHEADER_VERTICAL_MARGIN),
        }

        return text_to_div(Text('\n').join(self.subheaders), css_props)

    def to_html(self) -> str:
        css_props = {
            **DOC_DIV_CSS_PROPS,
            'margin-bottom': self.margin_bottom,
        }

        if self.background_color:
            css_props.update(HtmlStyle(f"on {self.background_color}").to_css)

        # Add more vertical margin before/after text messages  # TODO: this shouold be configured
        if isinstance(self.body_panel, BasePanel) and self.body_panel.is_list:
            css_props.update(margin_vertical_css(2))

        if self.is_table:
            body_html = one_row_table_html(self.body_panel, self.horizontal_body_margin_css)
        else:
            body_html = self.body_panel.to_div(self.body_margin_horizontal)

        elements = [
            self.file_info.to_div() if self.file_info else None,
            self.subheader_div,
            body_html,
        ]

        return div_tag(only_truthy(elements), css_props)

    def _align(self, element: RenderableType) -> RenderableType:
        return Align(element, self.justify) if self.justify else element

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Default `Document` renderer (Email and MessengerLog override this)."""
        # Set justify on the Text in the body panel
        if self.justify and not self.is_table and isinstance(self.body_panel.text, Text):
            self.body_panel.text.justify = self.justify

        indented_elemeents = [*self.justified_subheaders, self.body_panel]
        indented_elemeents = [Padding(e, self.body_margin) for e in indented_elemeents]
        indented_elemeents[-1].bottom = BOTTOM_PADDING
        elements = ([self.file_info] if self.file_info else []) + indented_elemeents

        for element in elements:
            yield self._align(element)
