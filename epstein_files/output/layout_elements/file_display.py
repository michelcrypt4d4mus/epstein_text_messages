from dataclasses import dataclass, field
from typing import Literal

from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.padding import Padding
from rich.text import Text
from rich.panel import Panel

from epstein_files.util.env import site_config

JustifyMethod = Literal['left', 'right']
BOTTOM_PADDING = 1


@dataclass
class FileDisplay:
    """Allows for proper right vs. left justify of a Document display."""
    file_info: Panel
    body_panel: Panel
    subheaders: list[Text] = field(default_factory=list)
    justify: JustifyMethod | None = None
    indent: int = 0

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

    def align(self, element: RenderableType) -> RenderableType:
        return Align(element, self.justify) if self.justify else element

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Default `Document` renderer (Email and MessengerLog override this)."""
        txt_elements = [*self.subheaders]

        if isinstance(self.body_panel.renderable, Text):
            txt_elements.append(self.body_panel.renderable)

        if self.justify:
            for txt in txt_elements:
                txt.justify = self.justify

        indented_elemeents = [*self.subheaders, self.body_panel]
        indented_elemeents = [Padding(e, self.padding) for e in indented_elemeents]
        indented_elemeents[-1].bottom = BOTTOM_PADDING
        elements = [self.file_info] + indented_elemeents

        for element in elements:
            yield self.align(element)
