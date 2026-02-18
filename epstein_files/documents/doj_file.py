import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Self

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.documents.doc_cfg import DebugDict
from epstein_files.documents.emails.constants import DOJ_EMAIL_OCR_REPAIRS, FALLBACK_TIMESTAMP
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.left_bar_panel import LeftBarPanel
from epstein_files.output.rich import RAINBOW, highlighter, wrap_in_markup_style
from epstein_files.util.logging import logger
from epstein_files.util.helpers.data_helpers import prefix_keys

EMPTY_LENGTH = 15
BAD_OCR_EMPTY_LENGTH = 150
IMAGE_PANEL_REGEX = re.compile(r"\n╭─* Page \d+, Image \d+.*?╯\n", re.DOTALL)
IGNORE_LINE_REGEX = re.compile(r"^(\d+\n?|[\s+❑]{2,})$")
MIN_VALID_LENGTH = 10
SINGLE_IMAGE_NO_TEXT = 'no text found in image(s)'
WORD_REGEX = re.compile(r"[A-Za-z]{3,}")

# From EFTA00000020 to EFTA00000344 there doesn't seem to be any text
BAD_OCR_ID_RANGES = [
    range(20, 345),
    range(347, 431),
    range(434, 646),
    range(652, 773),
    range(776, 843),
    range(846, 882),
    range(916, 1188),
    range(1189, 1335),
    range(1396, 1484),
    range(1735, 1888),
]

OTHER_DOC_URLS = {
    '245-22.pdf': 'https://www.justice.gov/multimedia/Court%20Records/Government%20of%20the%20United%20States%20Virgin%20Islands%20v.%20JPMorgan%20Chase%20Bank,%20N.A.,%20No.%20122-cv-10904%20(S.D.N.Y.%202022)/245-22.pdf'
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
    'EFTA00001347',
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
    'EFTA00002859',
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
    'EFTA00003074',
    'EFTA00001710',
    'EFTA00001427',
    'EFTA00000325',
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
    'EFTA00424931',
]

NO_IMAGE_SUFFIX = """
╭──── Page 1, Image 1 ─────╮
│ (no text found in image) │
╰──────────────────────────╯""".strip()

DEBUG_PROPS = [
    'is_bad_ocr',
]


@dataclass
class DojFile(OtherFile):
    """Class for the files released by DOJ on 2026-01-30 with `EFTA000` prefix."""
    _border_style: str | None = None

    # Class constants and variables
    MAX_TIMESTAMP: ClassVar[datetime] = datetime(2025, 1, 29)  # Cutoff for _extract_timestamp(), Overloads superclass
    border_style_rainbow_idx: ClassVar[int] = 0  # ClassVar to help change color as we print, no impact beyond fancier output

    @property
    def border_style(self) -> str:
        """Use a rainbow to make sure each printed object has different color for those before and after."""
        if self._border_style is None:
            self._border_style = RAINBOW[int(self.border_style_rainbow_idx % len(RAINBOW))]
            type(self).border_style_rainbow_idx += 1

        return self._border_style

    @property
    def empty_file_msg(self) -> RenderableType:
        """One line of linked text to show if this file doesn't seem to have any OCR text."""
        link_txt = Text('').append(Text.from_markup(super().external_link_markup))
        return Padding(link_txt.append(f" is a {SINGLE_IMAGE_NO_TEXT}..."), (0, 0, 0, 1))

    @property
    def external_link_markup(self) -> str:
        return wrap_in_markup_style(super().external_link_markup, self.border_style)

    @property
    def info(self) -> list[Text]:
        """Overloads superclass to adjust formatting."""
        return [Text(' ').append(sentence) for sentence in super().info]

    @property
    def is_bad_ocr(self) -> bool:
        if self.file_id in BAD_OCR_FILE_IDS:
            return True
        elif any(self.file_info.efta_id in r for r in BAD_OCR_ID_RANGES) and self.length < BAD_OCR_EMPTY_LENGTH:
            return True
        else:
            return not bool(WORD_REGEX.search(self.text))

    @property
    def is_empty(self) -> bool:
        """Overloads superclass method."""
        return len(self.text.strip().removesuffix(NO_IMAGE_SUFFIX)) < MIN_VALID_LENGTH

    @property
    def preview_text(self) -> str:
        """Text at start of file stripped of newlinesfor display in tables and other cramped settings."""
        return SINGLE_IMAGE_NO_TEXT if self.is_empty or self.is_bad_ocr else super().preview_text

    @property
    def preview_text_highlighted(self) -> Text:
        """Overloads superclass method."""
        if self.preview_text == SINGLE_IMAGE_NO_TEXT:
            return Text(self.preview_text, style='dim italic')
        else:
            return super().preview_text_highlighted

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

        if self.file_id in STRIP_IMAGE_PANEL_IDS:
            self.strip_image_ocr_panels()

    def external_links_txt(self, _style: str = '', include_alt_links: bool = True) -> Text:
        """Overrides super() method to apply self.border_style."""
        return self.file_info.external_links_txt(self.border_style, include_alt_links=include_alt_links)

    def strip_image_ocr_panels(self) -> None:
        """Removes the ╭--- Page 5, Image 1 ---- panels from the text."""
        new_text, num_replaced = IMAGE_PANEL_REGEX.subn('', self.text)
        self.warn(f"Stripped {num_replaced} image panels.")
        self._set_text(text=new_text)

    def _debug_props(self) -> DebugDict:
        props = super()._debug_props()
        props.update(prefix_keys(self._debug_prefix, self.truthy_props(DEBUG_PROPS)))
        return props

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
            self._set_text(lines=non_number_lines)

    def _repair(self) -> None:
        """Overloads superclass method."""
        new_text = self.repair_ocr_text(DOJ_EMAIL_OCR_REPAIRS, self.text)
        self._set_text(text=new_text)
        self._remove_number_only_lines()
