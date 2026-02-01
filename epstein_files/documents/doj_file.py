import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Self

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.document import INFO_INDENT, Document
from epstein_files.documents.email import Email
from epstein_files.documents.emails.email_header import FIELDS_COLON_PATTERN
from epstein_files.documents.other_file import Metadata, OtherFile
from epstein_files.util.constant.urls import doj_2026_file_url
from epstein_files.util.constants import FALLBACK_TIMESTAMP
from epstein_files.util.data import remove_zero_time
from epstein_files.util.logging import logger
from epstein_files.util.rich import RAINBOW, SKIPPED_FILE_MSG_PADDING, highlighter, link_text_obj

CHECK_LINK_FOR_DETAILS = 'not shown here, check original PDF for details'
IMAGE_PANEL_REGEX = re.compile(r"\n╭─* Page \d+, Image \d+.*?╯\n", re.DOTALL)
IGNORE_LINE_REGEX = re.compile(r"^(\d+\n?|[\s+❑]{2,})$")

# DojFile specific repair
OCR_REPAIRS: dict[str | re.Pattern, str] = {
    re.compile(fr"({FIELDS_COLON_PATTERN}.*\n)\nSubject:", re.MULTILINE): r'\1Subject:',
}

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
    'EFTA00008473',
    'EFTA00001846',
    'EFTA00000052',
    'EFTA00008445',
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
    'EFTA00039689': 'Dilorio emails to SEC about Signature Bank, Hapoalim, Bioptix / RIOT, Honig, etc.',
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
    """
    border_style_rainbow_idx: ClassVar[int] = 0  # ClassVar to help change color as we print, no impact beyond fancier output

    @property
    def is_bad_ocr(self) -> bool:
        return self.file_id in BAD_DOJ_FILE_IDS

    @property
    def is_empty(self) -> bool:
        """Overloads superclass method."""
        return len(self.text.strip().removesuffix(NO_IMAGE_SUFFIX)) < 20

    @property
    def timestamp_sort_key(self) -> tuple[datetime, str, int]:
        """Overloads parent method."""
        dupe_idx = 0
        # TODO: Years of 2001 are often garbage pared from '1.6' etc.
        sort_timestamp = self.timestamp or FALLBACK_TIMESTAMP
        sort_timestamp = FALLBACK_TIMESTAMP if sort_timestamp.year <= 2001 else sort_timestamp
        return (sort_timestamp, self.file_id, dupe_idx)

    def doj_link(self) -> Text:
        """Link to this file on the DOJ site."""
        return link_text_obj(doj_2026_file_url(self.doj_2026_dataset_id, self.url_slug), self.url_slug)

    def image_with_no_text_msg(self) -> RenderableType:
        """One line of linked text to show if this file doesn't seem to have any OCR text."""
        return Padding(
            Text('').append(self.doj_link()).append(f" is a single image with no text..."),
            SKIPPED_FILE_MSG_PADDING
        )

    def printable_doc(self) -> Self | Email:
        """Return a copy of this `DojFile` with simplified text if file ID is in `REPLACEMENT_TEXT`."""
        if self.file_id in REPLACEMENT_TEXT:
            replacement_text = f'(Text of "{REPLACEMENT_TEXT[self.file_id]}" {CHECK_LINK_FOR_DETAILS})'
            new_doj_file = type(self)(self.file_path)
            new_doj_file._set_computed_fields(text=replacement_text)
            return new_doj_file
        elif Document.is_email(self):
            return Email(self.file_path, text=self.text)  # Pass text= to avoid reprocessing
        else:
            return self

    def strip_image_ocr_panels(self) -> None:
        """Removes the ╭--- Page 5, Image 1 ---- panels from the text."""
        new_text, num_replaced = IMAGE_PANEL_REGEX.subn('', self.text)
        self.warn(f"Stripped {num_replaced} image panels.")
        self._set_computed_fields(text=new_text)

    def _border_style(self) -> str:
        """Color emails from Epstein to others with the color for the first recipient."""
        # Divide by 2 bc there's 2 calls for each DojFile, header panel and text
        style = RAINBOW[int(self.border_style_rainbow_idx % len(RAINBOW) / 2)]
        type(self).border_style_rainbow_idx += 1
        return style

    def _repair(self) -> None:
        if self.file_id == 'EFTA00006770':
            # Huge phone bill
            self.strip_image_ocr_panels()
            pages = self.text.split('MetroPCS')
            new_text = f"{pages[0]}\n\n(Redacted phone bill covering 2006-02-01 to 2006-06-16 {CHECK_LINK_FOR_DETAILS})"
            self._set_computed_fields(text=new_text)

        text = self.repair_ocr_text(OCR_REPAIRS, self.text)
        self._set_computed_fields(text=text)
        #print(f"WAS REPAIRED\n-------\n{self.text[0:5000]}\n-----")

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        doc = self.printable_doc()

        # Emails handle their own formatting
        if isinstance(doc, Email):
            yield doc
        else:
            for renderable in super().__rich_console__(console, options):
                yield renderable
