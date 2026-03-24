from dataclasses import dataclass, field
from typing import Literal

from rich.align import Align
from rich.console import Console, ConsoleOptions, JustifyMethod, RenderResult, RenderableType
from rich.padding import Padding, PaddingDimensions
from rich.table import Table
from rich.text import Text
from rich.panel import Panel

from epstein_files.output.html.builder import one_row_table_html, text_to_div, margin_vertical_css
from epstein_files.output.html.elements import div_class, div_tag, safe_padding
from epstein_files.output.html.rich_style import RichStyle
from epstein_files.output.html.positioned_rich import VERTICAL_MARGIN, PositionedRich, dimensions_to_margin_css
from epstein_files.output.layout_elements.base_panel import BasePanel
from epstein_files.output.layout_elements.list_panel import ListPanel
from epstein_files.util.env import site_config
from epstein_files.output.rich import indent_txt
from epstein_files.util.external_link import join_texts
from epstein_files.util.helpers.data_helpers import without_falsey

BOTTOM_PADDING = 1
SIDE_PANEL_WIDTH = 30
SUBHEADER_VERTICAL_MARGIN = 0.3

FLEX_CONTAINER_CSS = {
    'display': 'flex',
    'flex-direction': 'column',
}


@dataclass(kw_only=True)
class Layout:
    """Allows for proper right vs. left justify of a Document display."""
    background_color: str = ''
    body_indent: int | float = 0
    body_panel: BasePanel
    document: 'Document'
    file_info: BasePanel | None = None
    file_info_indent: int | float = 0
    indent: int | float = 0
    justify: JustifyMethod | None = None
    margin_bottom: float = VERTICAL_MARGIN  # Margin below the entire agglomeration of elements, not just the body
    side_panel: BasePanel | None = None
    subheaders: list[Text] = field(default_factory=list)

    def __post_init__(self):
        self.justify = None if self.justify in ['default', 'full'] else self.justify

        # copy background color to panel
        if self.background_color and isinstance(self.body_panel, BasePanel) and not self.body_panel.background_color:
            self.body_panel.background_color = self.background_color

        if self.file_info_indent:
            self.file_info.indent = self.file_info_indent

    @property
    def body_html(self) -> str:
        """Overload in subclass."""
        return self.body_panel.to_div(self.body_margin_horizontal)

    @property
    def body_margin(self) -> list[int | float]:
        """Margin for the body. Top/bottom always zero currrently."""
        padding = PositionedRich.zero_dimensions()

        # Usually subtle indent
        if self.justify == 'right':
            padding[1] = self.body_indent
        else:
            padding[3] = self.body_indent

        return padding

    @property
    def body_margin_horizontal(self) -> list[int | float]:
        """Just left and right margin, vertical margins are zeroed out."""
        margin_dimensions = self.body_margin
        margin_dimensions[0] = margin_dimensions[2] = 0
        return margin_dimensions

    @property
    def container_margin(self) -> list[int | float]:
        """The margins for the whole `Layout` including all panels."""
        margin = [0, 0, self.margin_bottom, 0]

        if self.justify == 'right':
            margin[1] = self.indent
        else:
            margin[3] = self.indent

        return margin

    @property
    def horizontal_body_margin_css(self) -> dict[str, str]:
        return dimensions_to_margin_css(self.body_margin_horizontal)

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

        # <fieldset> has weird margin spacing, this eliminates extra space between subheader and panel
        if not isinstance(self.body_panel, Table) and 'margin-bottom' in css_props:
            del css_props['margin-bottom']

        return text_to_div(Text('\n').join(self.subheaders), css_props)

    def side_panel_html(self) -> str:
        if self.side_panel:
            return self.side_panel.to_div(css={
                'margin-bottom': 'auto',
                'margin-left': 'auto',
                'margin-right': 'auto',
                'margin-top': 'auto',
            }, width=SIDE_PANEL_WIDTH)
        else:
            return ''

    def to_html(self) -> str:
        elements = without_falsey([
            self.file_info.to_div() if self.file_info else None,
            self.subheader_div,
        ])

        if (side_panel_html := self.side_panel_html()):
            inner_container = div_class([self.body_html, side_panel_html], 'horiz_container')
            elements.append(inner_container)
        else:
            elements.append(self.body_html)

        container_css = {
            **FLEX_CONTAINER_CSS,
            **dimensions_to_margin_css(self.container_margin),
        }

        return div_tag(elements, container_css)

    def _align(self, element: RenderableType) -> RenderableType:
        return Align(element, self.justify) if self.justify else element

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Default `Document` renderer (Email and MessengerLog override this)."""
        # Set justify on the Text in the body panel
        if self.justify and not isinstance(self.body_panel, Table) and isinstance(self.body_panel.text, Text):
            self.body_panel.text.justify = self.justify

        indented_elemeents = [*self.justified_subheaders, self.body_panel]
        indented_elemeents = [Padding(e, safe_padding(self.body_margin)) for e in indented_elemeents]
        indented_elemeents[-1].bottom = BOTTOM_PADDING
        elements = ([self.file_info] if self.file_info else []) + indented_elemeents

        for element in elements:
            element = Padding(element, safe_padding(self.container_margin)) if self.indent else element
            yield self._align(element)

    def __str__(self) -> str:
        return f"{type(self).__name__}('{self.document.file_id}')"


@dataclass(kw_only=True)
class TableLayout(Layout):
    body_panel: Table

    @property
    def body_html(self) -> str:
        return one_row_table_html(self.body_panel, self.horizontal_body_margin_css)
