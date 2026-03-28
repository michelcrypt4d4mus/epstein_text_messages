from dataclasses import dataclass, field
from typing import Literal

from rich.align import Align
from rich.console import Console, ConsoleOptions, JustifyMethod, RenderResult, RenderableType
from rich.padding import Padding, PaddingDimensions
from rich.text import Text
from rich.panel import Panel

from epstein_files.output.html.builder import OUTER_PANEL_DIV_PADDING_CSS, PANEL_BASE_PROPS, border_css_props, render_at_width, render_to_html
from epstein_files.output.html.elements import OptionalCssProps, div_class, div_with_legend, div_tag
from epstein_files.output.html.rich_style import RichStyle
from epstein_files.output.html.positioned_rich import CssProps, PositionedRich, dimensions_to_margin_css, dimensions_to_padding_css, margin_horizontal_css
from epstein_files.util.env import site_config
from epstein_files.util.external_link import join_texts
from epstein_files.util.helpers.data_helpers import without_falsey
from epstein_files.util.logging import logger


@dataclass(kw_only=True)
class BasePanel:
    """Basically for a <div>."""
    background_color: str = ''
    border_style: str
    document: 'Document | None' = None
    indent: int | float = 0
    max_width: int = 0
    padding: PaddingDimensions = 0
    text: Text
    title: Text | None = None
    title_justify: JustifyMethod = 'right'

    @property
    def color_css(self) -> CssProps:
        return RichStyle(self.style).to_css if self.style else {}

    @property
    def padding_css(self) -> CssProps:
        if self.padding:
            return dimensions_to_padding_css(self.padding)
        else:
            return OUTER_PANEL_DIV_PADDING_CSS

    @property
    def style(self) -> str:
        return f"on {self.background_color}" if self.background_color else ''

    def to_div(self, margins: list[int | float] | None = None, css: OptionalCssProps = None, width: int = 0) -> str:
        """Create an HTML <div> string for this panel."""
        render_width = width or self.max_width

        # Putting category in <div> class name changes the font depending on category
        if self.document and 'handwritten' in self.document._config.complete_description:
            css_category = 'handwritten'
        elif self.document and self.document.category:
            css_category = self.document.category
        else:
            css_category = ''

        return div_with_legend(
            contents=render_at_width(self.text, render_width) if render_width else render_to_html(self.text),
            legend=self.title.plain if self.title else '',  # TODO: make the title 'dim'
            css_props={
                **self._base_div_css(margins),
                **PANEL_BASE_PROPS,
                **border_css_props(self.border_style),
                **self.color_css,
                **self.padding_css,
                **(margin_horizontal_css(self.indent) if self.indent else {}),
                **(css or {}),
            },
            class_name=f"category_{css_category}" if css_category else ''
        )

    def _base_div_css(self, margins: list[int | float] | None = None) -> CssProps:
        return dimensions_to_margin_css(margins or PositionedRich.zero_dimensions())

    def __rich__(self) -> Panel | Padding:
        panel = Panel(
            self.text,
            border_style=self.border_style,
            expand=False,
            style=self.style,
            title=self.title,
            title_align=self.title_justify,
        )

        if self.indent:
            return Padding(panel, (0, int(self.indent)))
        else:
            return panel
