from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from rich.console import Console, ConsoleOptions, Group, JustifyMethod, RenderResult
from rich.text import Text

from epstein_files.documents.config.pic_cfg import PicCfg
from epstein_files.documents.document import Document
from epstein_files.output.html.html_dir import DEFAULT_HTML_DIR
from epstein_files.output.layout_elements.layout import Layout
from epstein_files.output.layout_elements.image_panel import ImagePanel


@dataclass
class Picture(Document):
    @classmethod
    def from_pic_cfg(cls, pic_cfg: PicCfg) -> Self:
        return cls(DEFAULT_HTML_DIR.joinpath('images', pic_cfg.image_filename))

    @property
    def colored_external_links(self) -> Text:
        """Overrides super() method to apply `self.author_style`."""
        return Text(self.file_id)

    def raw_text(self) -> str:
        """Reload the raw data from the underlying file and return it."""
        return str(self.file_id)

    def _repair(self) -> None:
        pass

    def formatted_info(self) -> dict[str, Text]:
        """Summary info about this document stylized and ready to work with."""
        info = {
            'file_id': Text(self.file_id),
            'type': Text('').append(self._class_name, style=self._class_style),
            'author': self.author_txt,
            'note': self._config.note_txt(False),
        }

        return info

    # def make_layout(
    #     self,
    #     justify: JustifyMethod = 'default',
    #     indent: int = 0,
    #     background_color: str = ''
    # ) -> Layout:
    #     """Allows for proper right vs. left justify."""
    #     panel_timestamp = Text(f"({self.panel_title_timestamp})", style='dim') if self.panel_title_timestamp else None

    #     if self._config.is_displayed_as_img:
    #         self._log(f"showing ImagePanel instead of text contents...")

    #         body_panel = ImagePanel(
    #             pic_cfg=self.config,
    #             text=self.prettified_txt,
    #             title=panel_timestamp
    #         )
    #     else:
    #         body_panel = BasePanel(
    #             border_style=self.border_style,
    #             document=self,
    #             max_width=MAX_BODY_PANEL_WIDTH,
    #             text=self.prettified_txt,
    #             title=panel_timestamp,
    #         )

    #     return Layout(
    #         background_color=self._config.background_color or background_color or DOC_PANEL_BG_COLOR,
    #         body_panel=body_panel,
    #         body_indent=site_config.indents.info,
    #         document=self,
    #         file_info=self.file_id_panel,
    #         indent=indent,
    #         justify=justify,
    #         margin_bottom=self.html_margin_bottom,
    #         side_panel=self.side_panel,
    #         subheaders=self.subheaders,
    #     )
