from dataclasses import dataclass, field
from typing import Literal

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from epstein_files.output.html.builder import (PANEL_BASE_PROPS, VERTICAL_MARGIN, border_css_props, rich_to_html,
     one_row_table_html, text_to_list, text_to_div, vertical_margin_props)
from epstein_files.output.html.elements import BLACK_BACKGROUND, div_class, div_with_legend, div_tag, to_em, side_props
from epstein_files.output.html.html_style import HtmlStyle
from epstein_files.output.rich import join_texts

JustifyMethod = Literal['center', 'left', 'right']

BOTTOM_PADDING = 1
SUBHEADER_VERTICAL_PADDING = to_em(0.3)

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

    def to_div(self, indents: tuple[int, int] | None = None) -> str:
        """Create an HTML <div> string for this panel."""
        indents = indents or (0, 0)
        div_props = {}

        if indents[0]:
            div_props.update(side_props('margin', ['left'], to_em(indents[0])))

        if indents[1]:
            div_props.update(side_props('margin', ['right'], to_em(indents[1])))

        # Handle MessengerLog / TextMessage list. # TODO this sucks
        if self.is_list:
            html = text_to_list(self.text, class_name='no_bullets')
            div_props.update({'word-wrap': 'break-word'})
            return div_class(html, BLACK_BACKGROUND, div_props)

        html = rich_to_html(self.text)
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
    indent: int = 0  # TODO: this should be a property of the BasePanel
    justify: JustifyMethod | None = None
    margin_bottom: str = VERTICAL_MARGIN
    subheaders: list[Text] = field(default_factory=list)

    @property
    def horizontal_body_margin(self) -> tuple[int, int]:
        """(left, right)"""
        return (self.margin[3], self.margin[1])

    @property
    def horizontal_body_margin_css_props(self) -> dict[str, str]:
        """(left, right)"""
        props = {}

        if self.horizontal_body_margin[0]:
            props.update(side_props('margin', ['left'], to_em(self.horizontal_body_margin[0])))
        if self.horizontal_body_margin[1]:
            props.update(side_props('margin', ['right'], to_em(self.horizontal_body_margin[1])))

        return props

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

    # TODO: rename body_margin?
    @property
    def margin(self) -> tuple[int, int, int, int]:
        """Margin for the body."""
        padding = [0, 0, 0, 0]

        # Set subtle indent
        if self.justify == 'right':
            padding[1] = self.indent
        else:
            padding[3] = self.indent

        return tuple(padding)

    @property
    def subheader_div(self) -> str:
        if not self.subheaders:
            return ''

        css_props = {
            **self.horizontal_body_margin_css_props,
            **vertical_margin_props(SUBHEADER_VERTICAL_PADDING),
        }

        return text_to_div(Text('\n').join(self.subheaders), css_props)

    def align(self, element: RenderableType) -> RenderableType:
        return Align(element, self.justify) if self.justify else element

    def to_html(self) -> str:
        if self.is_table:
            body_html = one_row_table_html(self.body_panel, self.horizontal_body_margin_css_props)
        else:
            body_html = self.body_panel.to_div(self.horizontal_body_margin)

        elements = [self.file_info.to_div()] if self.file_info else []
        elements.extend([self.subheader_div, body_html])

        inner_html = '\n'.join(elements)
        div_props = {**DOC_DIV_CSS_PROPS, 'margin-bottom': self.margin_bottom}

        if self.background_color:
            div_props.update(HtmlStyle(f"on {self.background_color}").to_css)

        # Add more vertical margin before/after text messages
        if isinstance(self.body_panel, BasePanel) and self.body_panel.is_list:
            div_props.update(vertical_margin_props(to_em(2)))

        return div_tag(inner_html, div_props)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Default `Document` renderer (Email and MessengerLog override this)."""
        # Set justify on the Text in the body panel
        if self.justify and not self.is_table and isinstance(self.body_panel.text, Text):
            self.body_panel.text.justify = self.justify

        indented_elemeents = [*self.justified_subheaders, self.body_panel]
        indented_elemeents = [Padding(e, self.margin) for e in indented_elemeents]
        indented_elemeents[-1].bottom = BOTTOM_PADDING
        elements = ([self.file_info] if self.file_info else []) + indented_elemeents

        for element in elements:
            yield self.align(element)
