import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Self

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.document import INFO_INDENT, Document
from epstein_files.documents.doj_files.full_text import EFTA00009622_TEXT
from epstein_files.documents.email import Email
from epstein_files.documents.emails.email_header import FIELDS_COLON_PATTERN
from epstein_files.documents.other_file import Metadata, OtherFile
from epstein_files.util.constants import FALLBACK_TIMESTAMP
from epstein_files.util.layout.left_bar_panel import LeftBarPanel
from epstein_files.util.logging import logger
from epstein_files.util.rich import RAINBOW, SKIPPED_FILE_MSG_PADDING, link_text_obj

CHECK_LINK_FOR_DETAILS = 'not shown here, check original PDF for details'
IMAGE_PANEL_REGEX = re.compile(r"\n╭─* Page \d+, Image \d+.*?╯\n", re.DOTALL)
IGNORE_LINE_REGEX = re.compile(r"^(\d+\n?|[\s+❑]{2,})$")

OTHER_DOC_URLS = {
    '245-22.pdf': 'https://www.justice.gov/multimedia/Court%20Records/Government%20of%20the%20United%20States%20Virgin%20Islands%20v.%20JPMorgan%20Chase%20Bank,%20N.A.,%20No.%20122-cv-10904%20(S.D.N.Y.%202022)/245-22.pdf'
}

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
    'EFTA00001940',
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
    'EFTA00001124',
    'EFTA00002509',
    'EFTA00008497',
    'EFTA00001031',
    'EFTA00005495',
    'EFTA00002830',
    'EFTA00001937',
    'EFTA00008496',
    'EFTA00008441',
    'EFTA00008415',
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
    'EFTA00008506',
]

PHONE_BILL_IDS = {
    'EFTA00006770': 'covering 2006-02-01 to 2006-06-16',
    'EFTA00006870': 'covering 2006-02-09 to 2006-07',
    'EFTA00006970': 'covering 2006-04-15 to 2006-07-16',
    # 'EFTA00007070':  # TODO: not a messy phone bill, short
}

REPLACEMENT_TEXT = {
    'EFTA00008120': '"Part II: The Art of Receiving a Massage"',
    'EFTA00008020': '"Massage for Dummies"',
    'EFTA00008220': '"Massage book: Chapter 11: Putting the Moves Together"',
    'EFTA00008320': '"Massage for Dummies (???)"',
    'EFTA00000476': 'Photo of JEFFREY EPSTEIN CASH DISBURSEMENTS for the month 2006-09',
    'EFTA00039312': 'Bureau of Prisons Program Statement / Memo about BOP Pharmacy Program',
    'EFTA00009622': EFTA00009622_TEXT,
    # TODO: move to PHONE_BILL_IDS
    'EFTA00006387': 'T-Mobile phone bill covering 2006-06-15 to 2006-07-23',
    'EFTA00007501': 'T-Mobile phone bill from 2005',
    'EFTA00006587': 'T-Mobile phone bill from 2006-09-04 to 2016-10-15',
    'EFTA00006687': 'T-Mobile phone bill from 2006-10-31 to 2006-12-25',
    'EFTA00007401': 'T-Mobile phone bill from 2004-08-25 to 2005-07-13',
    'EFTA00007301': 'T-Mobile response to subpoena March 23, 2007 - Blackberry phone logs for 2005',
    'EFTA00006487': 'T-Mobile phone bill 2006-08-26',
    'EFTA00006100': 'Palm Beach Police fax machine activity log 2005-12-28 to 2006-01-04',
    'EFTA00007253': 'T-Mobile response to subpoena March 23, 2007 - phone bill ',
}

INTERESTING_DOJ_FILES = {
    'EFTA02640711': 'Jabor Y home address (HBJ)',
    'EFTA00039689': 'Dilorio emails to SEC about Signature Bank, Hapoalim, Bioptix / RIOT, Honig, etc.',
    'EFTA00039025': 'Investigation and Review of the Federal Bureau of Prisons Custody, Care, and Supervision of Jeffrey Epstein',
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
    _border_style: str | None = None

    border_style_rainbow_idx: ClassVar[int] = 0  # ClassVar to help change color as we print, no impact beyond fancier output
    max_timestamp: ClassVar[datetime] = datetime(2025, 1, 29) # Overloaded in DojFile

    @property
    def border_style(self) -> str:
        """Use a rainbow to make sure each printed object has different color for those before and after."""
        if self._border_style is None:
            self._border_style = RAINBOW[int(self.border_style_rainbow_idx % len(RAINBOW))]
            type(self).border_style_rainbow_idx += 1

        return self._border_style

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
        return link_text_obj(self.external_url, self.url_slug)

    def external_links_txt(self, _style: str = '', include_alt_links: bool = True) -> Text:
        """Overrides super() method to apply self.author_style."""
        return super().external_links_txt(self.border_style, include_alt_links=include_alt_links)

    def image_with_no_text_msg(self) -> RenderableType:
        """One line of linked text to show if this file doesn't seem to have any OCR text."""
        return Padding(
            Text('').append(self.doj_link()).append(f" is a single image with no text..."),
            (0, 0, 0, 1)
        )

    def printable_doc(self) -> Self | Email:
        """Return a copy of this `DojFile` with simplified text if file ID is in `REPLACEMENT_TEXT`."""
        if Document.is_email(self):
            return Email(self.file_path, text=self.text)  # Pass text= to avoid reprocessing
        else:
            if self.file_id in PHONE_BILL_IDS:
                self.strip_image_ocr_panels()
                pages = self.text.split('MetroPCS')
                printable_text = f"{pages[0]}\n\n(Redacted phone bill {PHONE_BILL_IDS[self.file_id]} {CHECK_LINK_FOR_DETAILS})"
            elif self.file_id in REPLACEMENT_TEXT:
                printable_text = REPLACEMENT_TEXT[self.file_id]

                if len(printable_text) < 400:
                    printable_text = f'(Text of {printable_text} {CHECK_LINK_FOR_DETAILS})'
            else:
                printable_text = self.text

            self._set_computed_fields(text=printable_text)
            return self

    def strip_image_ocr_panels(self) -> None:
        """Removes the ╭--- Page 5, Image 1 ---- panels from the text."""
        new_text, num_replaced = IMAGE_PANEL_REGEX.subn('', self.text)
        self.warn(f"Stripped {num_replaced} image panels.")
        self._set_computed_fields(text=new_text)

    def _repair(self) -> None:
        """Overloads superclass method."""
        new_text = self.repair_ocr_text(OCR_REPAIRS, self.text)
        self._set_computed_fields(text=new_text)
        self._remove_number_only_lines()

    def _remove_number_only_lines(self) -> None:
        """Remove number only lines (which happen a lot in legal doc OCR) if there are more than a certain amount of them."""
        non_number_lines = [line for line in self.lines if not IGNORE_LINE_REGEX.match(line)]
        number_only_line_count = len(self.lines) - len(non_number_lines)

        if number_only_line_count > 20:
            logger.warning(f"{self.file_id}: Reduced line count from {len(self.lines)} to {len(non_number_lines)}")
            self._set_computed_fields(lines=non_number_lines)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        doc = self.printable_doc()

        # Emails handle their own formatting
        if isinstance(doc, Email):
            yield doc
        else:
            yield (info_panel := self.file_info_panel())
            border_style = info_panel.renderables[0].border_style
            panel_args = [self.text, border_style]

            if self.panel_title_timestamp:
                panel_args.append(Text(f"[{self.panel_title_timestamp}]", style='dim italic ' + border_style))

            table = LeftBarPanel.build(*panel_args)
            yield Padding(table, (0, 0, 1, 1))
