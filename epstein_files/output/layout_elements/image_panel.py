from dataclasses import dataclass, field

from rich.text import Text
from rich.panel import Panel

from epstein_files.output.html.builder import PANEL_BORDER_PROPS
from epstein_files.output.html.elements import OptionalCssProps, div_class, img
from epstein_files.output.html.positioned_rich import BLACK_BACKGROUND
from epstein_files.output.layout_elements.base_panel import BasePanel
from epstein_files.output.rich import indent_txt
from epstein_files.util.env import site_config
from epstein_files.util.external_link import join_texts
from epstein_files.util.helpers.data_helpers import without_falsey
from epstein_files.util.logging import logger

BORDER_RADIUS_CSS = {'border-radius': '20px'}
CSS_CLASS = f"{BLACK_BACKGROUND} img_panel"


@dataclass(kw_only=True)
class ImagePanel(BasePanel):
    """For <img>."""
    img_url: str

    def to_div(self, margins: list[int | float] | None = None, css: OptionalCssProps = None) -> str:
        """Create an HTML <div> string for this panel."""
        div_props = {
            **self._base_div_css(margins),
            **BORDER_RADIUS_CSS,
            **(css or {}),
        }

        return div_class(img(self.img_url, 'vertical', BORDER_RADIUS_CSS), CSS_CLASS, div_props)

    # def __rich__(self) -> str:
    #     logger.warning(f"__rich__() called on ImagePanel for {self.img_url}")
    #     return ''
