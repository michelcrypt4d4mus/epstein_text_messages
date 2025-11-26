import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from rich.text import Text

from util.constants import SEAN_BANNON, STEVE_BANNON
from util.file_helper import extract_file_id
from util.rich import ARCHIVE_LINK_COLOR, epsteinify_doc_url, highlight_names, logger, make_link, make_link_markup

MULTINEWLINE_REGEX = re.compile(r"\n{3,}")
WHITESPACE_REGEX = re.compile(r"\s{2,}|\t|\n", re.MULTILINE)
PREVIEW_CHARS = 520
GMAX_EMAIL = 'gmax1@ellmax.com'
JEEVACATION_GMAIL = 'jeevacation@gmail.com'
MIN_DOCUMENT_ID = 10477

OCR_REPAIRS = {
    'Follow me on twitter glhsummers': 'Follow me on twitter @lhsummers',
    'lndyke': 'Indyke',
    re.compile(r'from my BlackBerry[0°] wireless device'): 'from my BlackBerry® wireless device',
    re.compile(r'Sean Bannor?', re.I): SEAN_BANNON,
    re.compile(r'Steve Bannor]?', re.I): STEVE_BANNON,
    re.compile(r'gmax ?[1l] ?[@g]ellmax.c ?om'): GMAX_EMAIL,
    re.compile(r"[jl']ee[vy]acation[©@a(&,]{1,3}gmail.com"): JEEVACATION_GMAIL,
}


@dataclass
class Document:
    file_path: Path
    epsteinify_name_url: str = field(init=False)
    epsteinify_link_markup: str = field(init=False)
    file_id: str = field(init=False)
    filename: str = field(init=False)
    length: int = field(init=False)
    lines: list[str] = field(init=False)
    num_lines: int = field(init=False)
    text: str = field(init=False)

    def __post_init__(self):
        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)
        self.text = self._load_file()
        self.length = len(self.text)
        self.lines = self.text.split('\n')
        self.num_lines = len(self.lines)
        self.epsteinify_name_url = epsteinify_doc_url(self.file_path.stem)
        self.epsteinify_link_markup = make_link_markup(self.epsteinify_name_url, self.file_path.stem)

    def count_regex_matches(self, pattern: str) -> int:
        return len(re.findall(pattern, self.text))

    def epsteinify_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        return make_link(self.epsteinify_name_url, link_txt or self.filename, style)

    def highlighted_preview_text(self) -> Text:
        return Text.from_markup(highlight_names(self.preview_text()))

    def log_top_lines(self, n: int = 10, msg: str | None = None) -> None:
        msg = f"{msg + '. ' if msg else ''}Top lines of '{self.filename}' ({self.num_lines} lines):"
        logger.info(f"{msg}:\n\n{self.top_lines(n)}")

    def preview_text(self) -> str:
        return WHITESPACE_REGEX.sub(' ', self.text)[0:PREVIEW_CHARS]

    def top_lines(self, n: int = 10) -> str:
        return '\n'.join(self.lines[0:n])

    def _load_file(self):
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        with open(self.file_path) as f:
            text = f.read()
            text = text[1:] if (len(text) > 0 and text[0] == '\ufeff') else text  # remove BOM
            text = text.strip()

            for k, v in OCR_REPAIRS.items():
                if isinstance(k, re.Pattern):
                    text = k.sub(v, text)
                else:
                    text = text.replace(k, v)

            lines = [l.strip() for l in text.split('\n') if not l.startswith('HOUSE OVERSIGHT')]
            lines = lines[1:] if (len(lines) > 1 and lines[0] == '>>') else lines
            return MULTINEWLINE_REGEX.sub('\n\n\n', '\n'.join(lines))


@dataclass
class CommunicationDocument(Document):
    archive_link: Text = field(init=False)
    author: str | None = field(init=False)
    author_style: str = field(init=False)
    author_txt: Text = field(init=False)
    timestamp: datetime | None = field(init=False)

    def __post_init__(self):
        super().__post_init__()
