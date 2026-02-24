from copy import deepcopy
from dataclasses import dataclass, field
from typing import Literal

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.padding import Padding
from rich.text import Text
from rich.panel import Panel

from epstein_files.output.html.builder import PANEL_BASE_PROPS, border_css_props, in_padded_div, rich_to_html
from epstein_files.output.html.elements import CssUnit, div_tag, horizontal_margin_props, to_em, side_props
from epstein_files.output.rich import print_json
from epstein_files.util.env import site_config

JustifyMethod = Literal['center', 'left', 'right']

BOTTOM_PADDING = 1
VERTICAL_MARGIN = '10px'

DOC_DIV_CSS_PROPS = {
    'display': 'flex',
    'flex-direction': 'column',
    'margin-top': VERTICAL_MARGIN,
    'margin-bottom': VERTICAL_MARGIN,
}


@dataclass(kw_only=True)
class BasePanel:
    border_style: str
    text: Text
    title: Text | None = None
    title_justify: JustifyMethod = 'right'

    def to_div(self, indents: tuple[int, int] | None = None) -> str:
        """Create an HTML <div> string for this panel."""
        indents = indents or (0, 0)

        props = {
            **border_css_props(self.border_style),
            **PANEL_BASE_PROPS,
        }

        if indents[0]:
            props.update(side_props('margin', ['left'], to_em(indents[0])))
        if indents[1]:
            props.update(side_props('margin', ['right'], to_em(indents[1])))

        # print(f"indents: {indents}")
        print_json('div props', props)
        return div_tag(rich_to_html(self.text), props)

    def __rich__(self) -> Panel:
        return Panel(
            self.text,
            border_style=self.border_style,
            expand=False,
            title=self.title,
            title_align=self.title_justify,
        )


@dataclass(kw_only=True)
class FileDisplay:
    """Allows for proper right vs. left justify of a Document display."""
    body_panel: BasePanel
    file_info: BasePanel
    indent: int = 0
    justify: JustifyMethod | None = None
    subheaders: list[Text] = field(default_factory=list)

    @property
    def horizontal_padding(self) -> tuple[int, int]:
        """(left, right)"""
        return (self.padding[3], self.padding[1])

    @property
    def justified_subheaders(self) -> list[Text]:
        """Set justify `Text` to get right justification of text in right aligned elements."""
        subheaders = [txt.copy() for txt in self.subheaders]

        if self.justify:
            for txt in subheaders:
                txt.justify = self.justify

        return subheaders

    @property
    def padding(self) -> tuple[int, int, int, int]:
        padding = [0, 0, 0, 0]

        # Set subtle indent
        if self.justify == 'right':
            padding[1] = site_config.info_indent
            padding[3] = self.indent
        else:
            padding[1] = self.indent
            padding[3] = site_config.info_indent

        return tuple(padding)

    @property
    def subheader_div(self) -> str:
        if self.subheaders:
            return in_padded_div(Text('\n').join(self.subheaders))
        else:
            return ''

    def align(self, element: RenderableType) -> RenderableType:
        return Align(element, self.justify) if self.justify else element

    def to_html(self) -> str:
        elements = [
            self.file_info.to_div(),
            self.subheader_div,
            self.body_panel.to_div((1, 1)),
        ]

        inner_html = '\n'.join(elements)
        return div_tag(inner_html, DOC_DIV_CSS_PROPS)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Default `Document` renderer (Email and MessengerLog override this)."""
        # Set justify on the Text in the body panel
        if self.justify:
            self.body_panel.text.justify = self.justify

        indented_elemeents = [*self.justified_subheaders, self.body_panel]
        indented_elemeents = [Padding(e, self.padding) for e in indented_elemeents]
        indented_elemeents[-1].bottom = BOTTOM_PADDING
        elements = [self.file_info] + indented_elemeents

        for element in elements:
            yield self.align(element)
