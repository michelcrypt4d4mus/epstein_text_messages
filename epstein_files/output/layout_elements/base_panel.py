from dataclasses import dataclass, field
from typing import Literal

from rich.align import Align
from rich.console import Console, ConsoleOptions, JustifyMethod, RenderResult, RenderableType
from rich.padding import Padding, PaddingDimensions
from rich.text import Text
from rich.panel import Panel

from epstein_files.output.html.builder import PANEL_BASE_PROPS, border_css_props, render_to_html
from epstein_files.output.html.elements import OptionalCssProps, div_class, div_with_legend, div_tag
from epstein_files.output.html.rich_style import RichStyle
from epstein_files.output.html.positioned_rich import CssProps, PositionedRich, dimensions_to_margin_css, margin_horizontal_css
from epstein_files.util.env import site_config
from epstein_files.util.external_link import join_texts
from epstein_files.util.helpers.data_helpers import without_falsey


@dataclass(kw_only=True)
class BasePanel:
    """Basically for a <div>."""
    background_color: str = ''
    border_style: str
    indent: int | float = 0
    text: Text
    title: Text | None = None
    title_justify: JustifyMethod = 'right'

    @property
    def color_css(self) -> CssProps:
        return RichStyle(self.style).to_css if self.style else {}

    @property
    def style(self) -> str:
        return f"on {self.background_color}" if self.background_color else ''

    def to_div(self, margins: list[int | float] | None = None, css: OptionalCssProps = None) -> str:
        """Create an HTML <div> string for this panel."""
        div_props = {
            **self._base_div_css(margins),
            **PANEL_BASE_PROPS,
            **border_css_props(self.border_style),
            **self.color_css,
            **(margin_horizontal_css(self.indent) if self.indent else {}),
            **(css or {}),
        }

        # TODO: make the title 'dim'
        title = self.title.plain if self.title else ''
        return div_with_legend(render_to_html(self.text), title, div_props)

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
