from dataclasses import dataclass, field

from rich.text import Text
from rich.panel import Panel

from epstein_files.output.html.builder import border_css_props, render_to_html, text_to_list
from epstein_files.output.html.elements import OptionalCssProps, div_class
from epstein_files.output.html.positioned_rich import BLACK_BACKGROUND, VERTICAL_MARGIN, PositionedRich
from epstein_files.output.layout_elements.base_panel import BasePanel
from epstein_files.output.rich import indent_txt
from epstein_files.util.env import site_config
from epstein_files.util.external_link import join_texts
from epstein_files.util.helpers.data_helpers import without_falsey


@dataclass(kw_only=True)
class ListPanel(BasePanel):
    """For <ul> / <ol>."""
    text: list[Text]
    list_css_class: str = 'no_bullets'

    def to_div(self, margins: list[int | float] | None = None, css: OptionalCssProps = None, width: int = 0) -> str:
        """Create an HTML <div> string for this panel."""
        position = PositionedRich(self, margin=[VERTICAL_MARGIN, 0, VERTICAL_MARGIN, 0])

        div_props = {
            **self._base_div_css(margins),
            'word-wrap': 'break-word',
            **border_css_props(self.border_style),
            **self.color_css,
            **self.padding_css,
            **position.margins_vertical_css,
            **(css or {}),
        }

        html = render_to_html(self.title) if self.title else ''
        html += text_to_list(self.text, class_name=self.list_css_class)
        return div_class(html, BLACK_BACKGROUND, div_props)

    def __rich__(self) -> Panel | Text:
        txts = join_texts(self.text, '\n')

        if self.border_style or self.title:
            return Panel(
                txts,
                border_style=self.border_style,
                expand=False,
                title=self.title,
                title_align=self.title_justify,
            )
        else:
            return indent_txt(txts, site_config.indents.supressed_msg)
