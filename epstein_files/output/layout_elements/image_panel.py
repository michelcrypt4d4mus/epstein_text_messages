from dataclasses import dataclass, field

from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.config.pic_cfg import PicCfg
from epstein_files.output.html.elements import OptionalCssProps, div_class, img
from epstein_files.output.html.positioned_rich import BLACK_BACKGROUND
from epstein_files.output.layout_elements.base_panel import BasePanel
from epstein_files.output.rich import indent_txt
from epstein_files.util.constant.strings import DUMMY_ID
from epstein_files.util.env import site_config
from epstein_files.util.helpers.data_helpers import without_falsey
from epstein_files.util.logging import logger

BORDER_RADIUS_CSS = {'border-radius': '8px'}
CSS_CLASS = f"{BLACK_BACKGROUND} img_panel"
DEFAULT_IMAGE_BORDER_STYLE = ''


@dataclass(kw_only=True)
class ImagePanel(BasePanel):
    """For <img>."""
    border_style: str = DEFAULT_IMAGE_BORDER_STYLE
    pic_cfg: PicCfg = field(default_factory=lambda:PicCfg(id=DUMMY_ID))

    def to_div(self, margins: list[int | float] | None = None, css: OptionalCssProps = None, width: int = 0) -> str:
        """Create an HTML <div> string for this panel."""
        div_props = {
            **self._base_div_css(margins),
            **BORDER_RADIUS_CSS,
            **(css or {}),
        }

        return div_class(self.html_contents, CSS_CLASS, div_props)

    @property
    def html_contents(self) -> str:
        css_class = 'horizontal' if self.pic_cfg.is_horizontal else 'vertical'
        return img(self.pic_cfg.image_url, css_class, BORDER_RADIUS_CSS)
