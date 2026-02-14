import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Self

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.document import CHECK_LINK_FOR_DETAILS, Document
from epstein_files.documents.email import Email
from epstein_files.documents.emails.email_header import FIELDS_COLON_PATTERN
from epstein_files.documents.other_file import OtherFile
from epstein_files.util.constants import FALLBACK_TIMESTAMP
from epstein_files.util.layout.left_bar_panel import LeftBarPanel
from epstein_files.util.logging import logger
from epstein_files.util.rich import RAINBOW, highlighter, wrap_in_markup_style

IMAGE_PANEL_REGEX = re.compile(r"\n╭─* Page \d+, Image \d+.*?╯\n", re.DOTALL)
IGNORE_LINE_REGEX = re.compile(r"^(\d+\n?|[\s+❑]{2,})$")
MIN_VALID_LENGTH = 10
SINGLE_IMAGE_NO_TEXT = 'single image with no text'
WORD_REGEX = re.compile(r"[A-Za-z]{3,}")

OTHER_DOC_URLS = {
    '245-22.pdf': 'https://www.justice.gov/multimedia/Court%20Records/Government%20of%20the%20United%20States%20Virgin%20Islands%20v.%20JPMorgan%20Chase%20Bank,%20N.A.,%20No.%20122-cv-10904%20(S.D.N.Y.%202022)/245-22.pdf'
}

# DojFile specific repair
OCR_REPAIRS: dict[str | re.Pattern, str] = {
    re.compile(r"^Sent (Sun|Mon|Tue|Wed|Thu|Fri|Sat)", re.MULTILINE): r"Sent: \1",
    re.compile(fr"({FIELDS_COLON_PATTERN}.*\n)\nSubject:", re.MULTILINE): r'\1Subject:',
}

BAD_OCR_FILE_IDS = [
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
    'EFTA00001657',
    'EFTA00008495',
    'EFTA00001472',
    'EFTA00000677',
    'EFTA00000473',
    'EFTA00000587',
    'EFTA00000783',
    'EFTA00001669',
    'EFTA00001004',
    'EFTA00001808',
    'EFTA00001843',
    'EFTA00001845',
    'EFTA00003082',
    'EFTA00008413',
    'EFTA00002061',
    'EFTA00001809',
    'EFTA00002831',
    'EFTA00007864',
    'EFTA00003088',
    'EFTA00003091',
    'EFTA00002593',
    'EFTA00002133',
    'EFTA00001780',
    'EFTA00001633',
    'EFTA00001627',
    'EFTA00001539',
    'EFTA00001363',
    'EFTA00001276',
    'EFTA00001101',
    'EFTA00000563',
    'EFTA00002816',
    'EFTA00001114',
    'EFTA00008445',
    'EFTA00000476',
    'EFTA00001979',
    'EFTA00001655',
    'EFTA00001654',
    'EFTA00002229',
    'EFTA00002207',
    'EFTA00002203',
    'EFTA00001811',
    'EFTA00000675',
    'EFTA00001848',
    'EFTA00001803',
    'EFTA00008427',
    'EFTA00008503',
    'EFTA00008475',
    'EFTA00002463',
    'EFTA00002111',
    'EFTA00002804',
    'EFTA00002543',
    'EFTA00002830',
    'EFTA00002240',
    'EFTA00002538',
    'EFTA00002813',
    'EFTA00008411',
    'EFTA00008501',
    'EFTA00008511',
    'EFTA00008500',
    'EFTA00008480',
    'EFTA00008497',
    'EFTA00008493',
    'EFTA00008527',
    'EFTA00008519',
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
    'EFTA00000509',
    'EFTA00000514',
    'EFTA00000516',
    'EFTA00000531',
    'EFTA00000587',
    'EFTA00000635',
    'EFTA00000676',
    'EFTA00000776',
    'EFTA00000785',
    'EFTA00002061',
    'EFTA00001004',
    'EFTA00001063',
    'EFTA00002172',
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
    'EFTA00002342',
    'EFTA00000554',
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

STRIP_IMAGE_PANEL_IDS = [
    'EFTA00384774',
    'EFTA00007693',
    'EFTA02731361',
    'EFTA00002342',
    'EFTA00006374',
    'EFTA00007097',
    'EFTA00002342',
    'EFTA00007741',
    'EFTA00007893',
    'EFTA02731433',
    'EFTA00005731',
]

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
    def config_description(self) -> str | None:
        """Overloads superclass property."""
        if self.lines[0].lower() == 'valuation report':
            return f"Epstein investment portfolio valuation report"
        else:
            return super().config_description

    @property
    def external_link_markup(self) -> str:
        return wrap_in_markup_style(super().external_link_markup, self.border_style)

    @property
    def image_with_no_text_msg(self) -> RenderableType:
        """One line of linked text to show if this file doesn't seem to have any OCR text."""
        return Padding(
            Text('').append(Text.from_markup(super().external_link_markup)).append(f" is a {SINGLE_IMAGE_NO_TEXT}..."),
            (0, 0, 0, 1)
        )

    @property
    def preview_text_highlighted(self) -> Text:
        """Overloads superclass method."""
        if self.preview_text == SINGLE_IMAGE_NO_TEXT:
            return Text(self.preview_text, style='dim italic')
        else:
            return super().preview_text_highlighted

    @property
    def info(self) -> list[Text]:
        """Overloads superclass to adjust formatting."""
        return [Text(' ').append(sentence) for sentence in super().info]

    @property
    def is_bad_ocr(self) -> bool:
        if self.file_id in BAD_OCR_FILE_IDS:
            return True
        else:
            return not bool(WORD_REGEX.search(self.text))

    @property
    def is_empty(self) -> bool:
        """Overloads superclass method."""
        return len(self.text.strip().removesuffix(NO_IMAGE_SUFFIX)) < MIN_VALID_LENGTH

    @property
    def prettified_text(self) -> Text:
        """Returns the string we want to print as the body of the document."""
        if self.file_id in PHONE_BILL_IDS:
            pages = self.text.split('MetroPCS')
            text = f"{pages[0]}\n\n(Redacted phone bill {PHONE_BILL_IDS[self.file_id]} {CHECK_LINK_FOR_DETAILS})"
            return highlighter(text)
        else:
            return super().prettified_text

    @property
    def preview_text(self) -> str:
        """Text at start of file stripped of newlinesfor display in tables and other cramped settings."""
        if self.is_empty or self.is_bad_ocr:
            return SINGLE_IMAGE_NO_TEXT
        else:
            return super().preview_text

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

        if self.file_id in PHONE_BILL_IDS or self.file_id in STRIP_IMAGE_PANEL_IDS:
            self.strip_image_ocr_panels()

    def external_links_txt(self, _style: str = '', include_alt_links: bool = True) -> Text:
        """Overrides super() method to apply self.border_style."""
        return super().external_links_txt(self.border_style, include_alt_links=include_alt_links)

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

    def _left_bar_panel(self) -> RenderResult:
        """Alternate way of displaying DOJ files with a single color bar down the left side."""
        yield (info_panel := self.file_info_panel())
        border_style = info_panel.renderables[0].border_style
        panel_args = [self.prettified_text, border_style]

        if self.panel_title_timestamp:
            panel_args.append(Text(f"[{self.panel_title_timestamp}]", style='dim italic ' + border_style))

        table = LeftBarPanel.build(*panel_args)
        yield Padding(table, (0, 0, 1, 1))

    def _remove_number_only_lines(self) -> None:
        """Remove number only lines (which happen a lot in legal doc OCR) if there are more than a certain amount of them."""
        non_number_lines = [line for line in self.lines if not IGNORE_LINE_REGEX.match(line)]
        number_only_line_count = len(self.lines) - len(non_number_lines)

        if number_only_line_count > 20:
            self.warn(f"Reduced line count from {len(self.lines)} to {len(non_number_lines)} by stripping number only lines")
            self._set_computed_fields(lines=non_number_lines)

    def _repair(self) -> None:
        """Overloads superclass method."""
        new_text = self.repair_ocr_text(OCR_REPAIRS, self.text)
        self._set_computed_fields(text=new_text)
        self._remove_number_only_lines()
