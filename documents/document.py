import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from rich.markup import escape
from rich.text import Text

from util.constants import HOUSE_OVERSIGHT_PREFIX, search_archive_url
from util.data import patternize
from util.env import logger
from util.file_helper import extract_file_id
from util.rich import (ARCHIVE_LINK_COLOR, epsteinify_doc_url, highlight_regex_match, highlighter,
     logger, make_link, make_link_markup)
from util.strings import *

MULTINEWLINE_REGEX = re.compile(r"\n{3,}")
TIMESTAMP_SECONDS_REGEX = re.compile(r":\d{2}$")
WHITESPACE_REGEX = re.compile(r"\s{2,}|\t|\n", re.MULTILINE)
HOUSE_OVERSIGHT = 'HOUSE OVERSIGHT'
MIN_DOCUMENT_ID = 10477
PREVIEW_CHARS = 520

# Takes ~1.1 seconds to apply these repairs
OCR_REPAIRS = {
    re.compile(r'\.corn\b'): '.com',
    'lndyke': 'Indyke',
    'Nil Priell': 'Nili Priell',
}

FILENAME_MATCH_STYLES = [
    'dark_green',
    'green',
    'spring_green4',
]


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

    file_matching_idx: ClassVar[int] = 0

    def __post_init__(self):
        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)
        self.text = self._load_file()
        self._set_computed_fields()
        self.epsteinify_name_url = epsteinify_doc_url(self.file_path.stem)  # URL to search epsteinify for the filename
        self.epsteinify_link_markup = make_link_markup(self.epsteinify_name_url, self.file_path.stem)

    def archive_link(self, link_txt: str | None = None, style: str = ARCHIVE_LINK_COLOR) -> Text:
        """Link to search courier newsroom Google drive."""
        return make_link(search_archive_url(self.filename), link_txt or self.filename, style)

    def count_regex_matches(self, pattern: str) -> int:
        return len(re.findall(pattern, self.text))

    def epsteinify_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        return make_link(self.epsteinify_name_url, link_txt or self.filename, style)

    def highlighted_preview_text(self) -> Text:
        try:
            return highlighter(escape(self.preview_text()))
        except Exception as e:
            logger.error(f"Failed to apply markup in string '{escape_single_quotes(self.preview_text())}'\n"
                         f"Original string: '{escape_single_quotes(self.preview_text())}'\n"
                         f"File: '{self.filename}'\n")

            return Text(escape(self.preview_text()))

    def lines_matching(self, _pattern: re.Pattern | str) -> list[str]:
        pattern = patternize(_pattern)
        return [f"{self.file_path.name}:{line}" for line in self.lines if pattern.search(line)]

    def lines_matching_txt(self, _pattern: re.Pattern | str) -> list[Text]:
        pattern = patternize(_pattern)
        matched_lines = [line for line in self.lines if pattern.search(line)]

        if len(matched_lines) == 0:
            return []

        file_style = FILENAME_MATCH_STYLES[type(self).file_matching_idx % len(FILENAME_MATCH_STYLES)]
        type(self).file_matching_idx += 1

        return [
            Text('').append(self.file_path.name, style=file_style).append(':').append(highlight_regex_match(line, pattern))
            for line in matched_lines
        ]

    def regex_repair_text(self, repairs: dict[str | re.Pattern, str], text: str) -> str:
        for k, v in repairs.items():
            if isinstance(k, re.Pattern):
                text = k.sub(v, text)
            else:
                text = text.replace(k, v)

        return text

    def log_top_lines(self, n: int = 10, msg: str | None = None) -> None:
        msg = f"{msg + '. ' if msg else ''}Top lines of '{self.filename}' ({self.num_lines} lines):"
        logger.info(f"{msg}:\n\n{self.top_lines(n)}")

    def preview_text(self) -> str:
        return WHITESPACE_REGEX.sub(' ', self.text)[0:PREVIEW_CHARS]

    def top_lines(self, n: int = 10) -> str:
        return '\n'.join(self.lines[0:n])

    def write_clean_text(self, output_path: Path) -> None:
        if output_path.exists():
            if str(output_path.name).startswith(HOUSE_OVERSIGHT_PREFIX):
                raise RuntimeError(f"'{output_path}' already exists! Not overwriting.")
            else:
                logger.warning(f"Overwriting '{output_path}'...")

        with open(output_path, 'w') as f:
            f.write(self.text)

        logger.warning(f"Wrote {self.length} chars of cleaned {self.filename} to {output_path}.")

    def _load_file(self):
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        with open(self.file_path) as f:
            text = f.read()
            text = text[1:] if (len(text) > 0 and text[0] == '\ufeff') else text  # remove BOM
            text = self.regex_repair_text(OCR_REPAIRS, text.strip())
            lines = [l.strip() for l in text.split('\n') if not l.startswith(HOUSE_OVERSIGHT)]
            lines = lines[1:] if (len(lines) > 1 and lines[0] == '>>') else lines
            return MULTINEWLINE_REGEX.sub('\n\n\n', '\n'.join(lines))

    def _set_computed_fields(self) -> None:
        self.length = len(self.text)
        self.lines = self.text.split('\n')
        self.num_lines = len(self.lines)


@dataclass
class CommunicationDocument(Document):
    archive_link: Text = field(init=False)
    author: str | None = field(init=False)
    author_style: str = field(init=False)
    author_txt: Text = field(init=False)
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        super().__post_init__()

    def timestamp_without_seconds(self) -> str:
        return TIMESTAMP_SECONDS_REGEX.sub('', str(self.timestamp))
