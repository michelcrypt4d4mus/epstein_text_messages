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
from epstein_files.util.constant.names import RENATA_BOLOTOVA
from epstein_files.util.constants import FALLBACK_TIMESTAMP
from epstein_files.util.data import without_falsey
from epstein_files.util.layout.left_bar_panel import LeftBarPanel
from epstein_files.util.logging import logger
from epstein_files.util.rich import RAINBOW, INFO_STYLE, SKIPPED_FILE_MSG_PADDING, highlighter, link_text_obj

CHECK_LINK_FOR_DETAILS = 'not shown here, check original PDF for details'
IMAGE_PANEL_REGEX = re.compile(r"\n╭─* Page \d+, Image \d+.*?╯\n", re.DOTALL)
IGNORE_LINE_REGEX = re.compile(r"^(\d+\n?|[\s+❑]{2,})$")
MIN_VALID_LENGTH = 10

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
    'EFTA00008512',
    'EFTA00008513',
    'EFTA00008495',
    'EFTA00008494',
    'EFTA00008469',
    'EFTA00008461',
    'EFTA00008453',
    'EFTA00008443',
    'EFTA00008427',
    'EFTA00005899',
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
    'EFTA00001368',
    'EFTA00000134',
    'EFTA00000471',
    'EFTA00001848',
    'EFTA00008506',
]

PHONE_BILL_IDS = {
    'EFTA00006770': 'covering 2006-02-01 to 2006-06-16',
    'EFTA00006870': 'covering 2006-02-09 to 2006-07',
    'EFTA00006970': 'covering 2006-04-15 to 2006-07-16',
    # 'EFTA00007070':  # TODO: not a messy phone bill, short, has additional info at end
}

INTERESTING_DOJ_FILES = {
    'EFTA02640711': 'Jabor Y home address (HBJ)',
    'EFTA00039689': 'Dilorio emails to SEC about Signature Bank, Hapoalim, Bioptix / RIOT, Honig, etc.',
    'EFTA00039025': 'Investigation and Review of the Federal Bureau of Prisons Custody, Care, and Supervision of Jeffrey Epstein',
    'EFTA02296929': f"{RENATA_BOLOTOVA} appears to know Epstein's final girlfriend",
    'EFTA01273102': f"payment from Epstein to {RENATA_BOLOTOVA}'s father's account at Sberbank",
    'EFTA02725909': 'presentation to NYDFS for "NYC Bitcoin Exchanges" with Balaji Srinivisan and Andrew Farkas on the board',
    'EFTA01622387': f"{RENATA_BOLOTOVA} iMessage conversation",
    'EFTA00810239': "Peter Thiel fund Valar Ventures pitch deck",
    'EFTA00810510': "Peter Thiel fund Valar Ventures Fall 2016 Update",
    'EFTA00810474': "Peter Thiel fund Valar Ventures Fall 2018 Update",
    'EFTA00836182': "Peter Thiel fund Valar Ventures Limited Partners email",
    'EFTA01003346': "Peter Thiel tells Epstein to invest in his fund",
    'EFTA00811866': "list of Epstein's bank accounts",
    'EFTA00811666': "asset valuations of Epstein's holdings, includes 'Coinbase via grat'",
    'EFTA00803405': "Honeycomb Asset Management (Spotify and Tencent investors) 2018 firm brochure",
    'EFTA00803491': "Honeycomb Asset Management (Spotify and Tencent investors) deck",
    'EFTA00803459': "Honeycomb Asset Management (Spotify and Tencent investors) January 2019 report",
    'EFTA00603445': "Honeycomb Asset Management (Spotify and Tencent investors) July 2017 report",
    'EFTA00803464': "Honeycomb Asset Management (Spotify and Tencent investors) July 2018 report",
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
    def info(self) -> list[Text]:
        """Overloads superclass to adjust formatting."""
        return [Text(' ').append(sentence) for sentence in super().info]

    @property
    def is_bad_ocr(self) -> bool:
        return self.file_id in BAD_DOJ_FILE_IDS

    @property
    def is_empty(self) -> bool:
        """Overloads superclass method."""
        return len(self.text.strip().removesuffix(NO_IMAGE_SUFFIX)) < MIN_VALID_LENGTH

    @property
    def prettified_text(self) -> Text:
        """Returns the string we want to print as the body of the document."""
        style = ''

        if self.file_id in PHONE_BILL_IDS:
            pages = self.text.split('MetroPCS')
            text = f"{pages[0]}\n\n(Redacted phone bill {PHONE_BILL_IDS[self.file_id]} {CHECK_LINK_FOR_DETAILS})"
        elif self.config and self.config.replace_text_with:
            if len(self.config.replace_text_with) < 300:
                style = INFO_STYLE
                text = f'(Text of {self.config.replace_text_with} {CHECK_LINK_FOR_DETAILS})'
            else:
                text = self.config.replace_text_with
        else:
            text = self.text

        return Text(text, style)

    @property
    def timestamp_sort_key(self) -> tuple[datetime, str, int]:
        """Overloads parent method."""
        dupe_idx = 0
        # TODO: Years of 2001 are often garbage pared from '1.6' etc.
        sort_timestamp = self.timestamp or FALLBACK_TIMESTAMP
        sort_timestamp = FALLBACK_TIMESTAMP if sort_timestamp.year <= 2001 else sort_timestamp
        return (sort_timestamp, self.file_id, dupe_idx)

    def __post_init__(self):
        super().__post_init__()

        if self.file_id in PHONE_BILL_IDS:
            self.strip_image_ocr_panels()

    def doj_link(self) -> Text:
        """Link to this file on the DOJ site."""
        return link_text_obj(self.external_url, self.url_slug)

    def external_links_txt(self, _style: str = '', include_alt_links: bool = True) -> Text:
        """Overrides super() method to apply self.border_style."""
        return super().external_links_txt(self.border_style, include_alt_links=include_alt_links)

    def image_with_no_text_msg(self) -> RenderableType:
        """One line of linked text to show if this file doesn't seem to have any OCR text."""
        return Padding(
            Text('').append(self.doj_link()).append(f" is a single image with no text..."),
            (0, 0, 0, 1)
        )

    def printable_document(self) -> Self | Email:
        """Return a copy of this `DojFile` with simplified text if file ID is in `REPLACEMENT_TEXT`."""
        if Document.is_email(self):
            try:
                return Email(self.file_path, text=self.text)  # Pass text= to avoid reprocessing
            except Exception as e:
                self.warn(f"Error creating Email object, trying full reload of text...")
                return Email(self.file_path)
        else:
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
            self.warn(f"Reduced line count from {len(self.lines)} to {len(non_number_lines)}")
            self._set_computed_fields(lines=non_number_lines)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        doc = self.printable_document()

        # Emails handle their own formatting
        if isinstance(doc, Email):
            yield doc
        else:
            yield (info_panel := self.file_info_panel())
            border_style = info_panel.renderables[0].border_style
            panel_args = [self.prettified_text, border_style]

            if self.panel_title_timestamp:
                panel_args.append(Text(f"[{self.panel_title_timestamp}]", style='dim italic ' + border_style))

            table = LeftBarPanel.build(*panel_args)
            yield Padding(table, (0, 0, 1, 1))
