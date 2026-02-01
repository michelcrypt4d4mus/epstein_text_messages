from copy import deepcopy
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from rich.align import Align
from rich.columns import Columns
from rich.console import Console, ConsoleOptions, Group, RenderableType, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.document import INFO_INDENT, INFO_PADDING
from epstein_files.documents.other_file import Metadata, OtherFile
from epstein_files.util.constant.urls import ARCHIVE_LINK_COLOR, doj_2026_file_url
from epstein_files.util.constants import ALL_FILE_CONFIGS, FALLBACK_TIMESTAMP
from epstein_files.util.doc_cfg import DocCfg
from epstein_files.util.logging import logger
from epstein_files.util.rich import RAINBOW, SKIPPED_FILE_MSG_PADDING, highlighter, join_texts, link_text_obj

DATASET_ID_REGEX = re.compile(r"(?:epstein_dataset_|DataSet )(\d+)")
IGNORE_LINE_REGEX = re.compile(r"^(\d+\n?|[\s+❑]{2,})$")

BAD_DOJ_FILE_IDS = [
    'EFTA00008511',
    'EFTA00008503',
    'EFTA00002512',
    'EFTA00008501',
    'EFTA00008500',
    'EFTA00008514',
    'EFTA00008410',
    'EFTA00008411',
    'EFTA00008519',
    'EFTA00008493',
    'EFTA00008527',
    'EFTA00008480',
    'EFTA00008497',
    'EFTA00001031',
    'EFTA00005495',
    'EFTA00002830',
    'EFTA00008496',
    'EFTA00008441',
    'EFTA00000675',
    'EFTA00002538',
    'EFTA00000672',
    'EFTA00002814',
    'EFTA00002812',
    'EFTA00002543',
    'EFTA00002813',
    'EFTA00002523',
    'EFTA00002079',
    'EFTA00002805',
    'EFTA00001840',
    'EFTA00001114',
    'EFTA00002812',
    'EFTA00002543',
    'EFTA00002786',
    'EFTA00001271',
    'EFTA00002523',
    'EFTA00001979',
    'EFTA00002110',
    'EFTA00008504',
    'EFTA00000134',
    'EFTA00000471',
    'EFTA00001848',
]

REPLACEMENT_TEXT = {
    'EFTA00008120': 'Part II: The Art of Receiving a Massage',
    'EFTA00008020': 'Massage for Dummies',
    'EFTA00008220': 'Massage book: Chapter 11: Putting the Moves Together',
    'EFTA00008320': 'Massage for Dummies (???)',
}

INTERESTING_DOJ_FILES = {
    'EFTA02640711': 'Jabor Y home address (HBJ)',
}

NO_IMAGE_SUFFIX = """
╭──── Page 1, Image 1 ─────╮
│ (no text found in image) │
╰──────────────────────────╯
""".strip()


@dataclass
class DojFile(OtherFile):
    """
    Class for the files released by DOJ on 2026-01-30 with `EFTA000` prefix.

    Attributes:
        doj_2026_dataset_id (int): The ID of the DataSet the DOJ released this file in. Important for links.
    """
    file_path: Path
    doj_2026_dataset_id: int = field(init=False)

    # For fancy coloring only
    border_style_rainbow_idx: ClassVar[int] = 0

    @property
    def is_bad_ocr(self) -> bool:
        return self.file_id in BAD_DOJ_FILE_IDS

    def __post_init__(self):
        super().__post_init__()

        if (data_set_match := DATASET_ID_REGEX.search(str(self.file_path))):
            self.doj_2026_dataset_id = int(data_set_match.group(1))
            logger.info(f"Extracted data set number {self.doj_2026_dataset_id} for {self.url_slug}")

    def doj_link(self) -> Text:
        """Link to this file on the DOJ site."""
        return link_text_obj(doj_2026_file_url(self.doj_2026_dataset_id, self.url_slug), self.url_slug)

    def external_links_txt(self, style: str = '', include_alt_links: bool = False) -> Text:
        """Overloads superclass method."""
        links = [self.doj_link()]
        base_txt = Text('', style='white' if include_alt_links else ARCHIVE_LINK_COLOR)
        return base_txt.append(join_texts(links))

    def image_with_no_text_msg(self) -> RenderableType:
        """One line of linked text to show if this file doesn't seem to have any OCR text."""
        return Padding(
            Text('').append(self.doj_link()).append(f" is a single image with no text..."),
            SKIPPED_FILE_MSG_PADDING
        )

    def is_empty(self) -> bool:
        """Overloads superclass method."""
        return len(self.text.strip().removesuffix(NO_IMAGE_SUFFIX)) < 20

    def prep_for_printing(self) -> None:
        """Replace some fields and strip out some lines, but do it only before printing (don't store to pickled file)."""
        if self.file_id in REPLACEMENT_TEXT:
            self._set_computed_fields(text=f'(Text of "{REPLACEMENT_TEXT[self.file_id]}" not shown here, check link for PDF)')
            return

        non_number_lines = [line for line in self.lines if not IGNORE_LINE_REGEX.match(line)]

        if len(non_number_lines) != len(self.lines):
            logger.warning(f"{self.file_id}: Reduced line count from {len(self.lines)} to {len(non_number_lines)}")
            self._set_computed_fields(lines=non_number_lines)

    def timestamp_sort_key(self) -> tuple[datetime, str, int]:
        """Overloads parent method."""
        dupe_idx = 0
        # TODO: Years of 2001 are often garbage pared from '1.6' etc.
        sort_timestamp = self.timestamp or FALLBACK_TIMESTAMP
        sort_timestamp = FALLBACK_TIMESTAMP if sort_timestamp.year <= 2001 else sort_timestamp
        return (sort_timestamp, self.file_id, dupe_idx)

    def _border_style(self) -> str:
        """Color emails from epstein to others with the color for the first recipient."""
        style = RAINBOW[self.border_style_rainbow_idx % len(RAINBOW)]
        type(self).border_style_rainbow_idx += 1
        return style

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        info_panel = self.file_info_panel()
        timestamp_txt = Text(f'(inferred timestamp: ', style='dim').append(str(self.timestamp)).append(')')

        yield info_panel
        yield Padding(timestamp_txt, INFO_PADDING)
        text_panel = Panel(highlighter(self.text), border_style=info_panel._renderables[0].border_style, expand=False)
        yield Padding(text_panel, (0, 0, 1, INFO_INDENT))
