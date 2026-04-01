from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from rich.text import Text

from epstein_files.documents.config.pic_cfg import PicCfg
from epstein_files.documents.document import Document
from epstein_files.output.html.html_dir import DEFAULT_HTML_DIR
from epstein_files.output.layout_elements.base_panel import BasePanel
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

    @property
    def file_id_panel(self) -> BasePanel | None:
        """The header panel printed before the body and subheaders with links and file ID etc."""
        return None

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
            'note': self._config.note_txt(include_category=False),
        }

        return info

    @classmethod
    def default_category(cls) -> str:
        return cls.__name__.lower()
