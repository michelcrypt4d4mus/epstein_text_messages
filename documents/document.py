import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from rich.text import Text

from util.file_helper import extract_file_id
from util.rich import ARCHIVE_LINK_COLOR, epsteinify_doc_url, logger, make_link

MULTINEWLINE_REGEX = re.compile(r"\n{3,}")
GMAX_EMAIL = 'gmax1@ellmax.com'
JEEVACATION_GMAIL = 'jeevacation@gmail.com'

OCR_REPAIRS = {
    'lndyke': 'Indyke',
    'gmaxlgellmax.com': GMAX_EMAIL,
    'gmaxl@ellmax.com': GMAX_EMAIL,
    'jeevacation©gmail.com': JEEVACATION_GMAIL,
    'jeevacationagmail.com': JEEVACATION_GMAIL,
    'jeeyacation@gmail.com': JEEVACATION_GMAIL,
    'jeevacation@,gmail.com': JEEVACATION_GMAIL,
}


@dataclass
class Document:
    file_path: Path
    epsteinify_url: str = field(init=False)
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
        self.epsteinify_url = epsteinify_doc_url(self.file_path.stem)

    def count_regex_matches(self, pattern: str) -> int:
        return len(re.findall(pattern, self.text))

    def epsteinify_link(self, style: str = ARCHIVE_LINK_COLOR) -> Text:
        return make_link(self.epsteinify_url, self.filename, style)

    def log_top_lines(self, n: int = 10, msg: str | None = None) -> None:
        msg = f"{msg + '. ' if msg else ''}Top lines of '{self.filename}' ({self.num_lines} lines):"
        logger.info(f"{msg}:\n\n{self.top_lines(n)}")

    def top_lines(self, n: int = 10) -> str:
        return '\n'.join(self.lines[0:n])

    def _load_file(self):
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        with open(self.file_path) as f:
            text = f.read()
            text = text[1:] if (len(text) > 0 and text[0] == '\ufeff') else text  # remove BOM
            text = text.strip()

            for k, v in OCR_REPAIRS.items():
                text = text.replace(k, v)

            lines = [l.strip() for l in text.split('\n') if not l.startswith('HOUSE OVERSIGHT')]
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
