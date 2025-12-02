import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from subprocess import run
from typing import ClassVar

from rich.markup import escape
from rich.text import Text

from util.constants import HOUSE_OVERSIGHT_PREFIX, esptein_web_doc_url, search_archive_url
from util.data import collapse_newlines, patternize
from util.env import args, logger
from util.file_helper import DOCS_DIR, build_filename_for_id, extract_file_id, is_local_extract_file
from util.rich import (ARCHIVE_LINK_COLOR, console, epsteinify_doc_url, highlight_regex_match, highlighter,
     logger, make_link, make_link_markup)
from util.strings import *

TIMESTAMP_SECONDS_REGEX = re.compile(r":\d{2}$")
WHITESPACE_REGEX = re.compile(r"\s{2,}|\t|\n", re.MULTILINE)
HOUSE_OVERSIGHT = HOUSE_OVERSIGHT_PREFIX.replace('_', ' ').strip()
MIN_DOCUMENT_ID = 10477
PREVIEW_CHARS = 520
KB = 1024
MB = KB * KB

# Subclass names
DOCUMENT = 'Document'
EMAIL = 'Email'
MESSENGER_LOG = 'MessengerLog'

DOC_TYPE_STYLES = {
    DOCUMENT: 'grey69',
    EMAIL: 'sea_green2',
    MESSENGER_LOG: 'cyan',
}

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
    epsteinify_doc_url: str = field(init=False)
    epsteinify_link_markup: str = field(init=False)
    epstein_web_doc_link_markup: str = field(init=False)
    file_id: str = field(init=False)
    filename: str = field(init=False)
    length: int = field(init=False)
    lines: list[str] = field(init=False)
    num_lines: int = field(init=False)
    text: str = field(init=False)
    url_slug: str = field(init=False)  # e.g. 'HOUSE_OVERSIGHT_123456

    file_matching_idx: ClassVar[int] = 0

    def __post_init__(self):
        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)

        if is_local_extract_file(self.filename):
            self.url_slug = build_filename_for_id(self.file_id)
        else:
            self.url_slug = self.file_path.stem

        self.text = self._load_file()
        self._set_computed_fields()
        self.epsteinify_doc_url = epsteinify_doc_url(self.url_slug)
        self.epsteinify_link_markup = make_link_markup(self.epsteinify_doc_url, self.file_path.stem)
        self.epstein_web_doc_url = esptein_web_doc_url(self.url_slug)
        self.epstein_web_doc_link_markup = make_link_markup(self.epstein_web_doc_url, self.file_path.stem)

    def courier_archive_link(self, link_txt: str | None = None, style: str = ARCHIVE_LINK_COLOR) -> Text:
        """Link to search courier newsroom Google drive."""
        return make_link(search_archive_url(self.filename), link_txt or self.filename, style)

    def count_regex_matches(self, pattern: str) -> int:
        return len(re.findall(pattern, self.text))

    def description(self) -> Text:
        doc_type = str(type(self).__name__)
        txt = Text('').append(self.file_path.stem, style='bright_green')
        txt.append(f' {doc_type} ', style=DOC_TYPE_STYLES[doc_type]).append(f"(num_lines=")
        txt.append(f"{self.num_lines:,}", style='cyan').append(", size=")
        txt.append(self.size_str(), style='aquamarine1')

        if doc_type == DOCUMENT:
            txt.append(')')

        return txt

    def epsteinify_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        return make_link(self.epsteinify_doc_url, link_txt or self.file_path.stem, style)

    def epstein_web_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        return make_link(self.epstein_web_doc_url, link_txt or self.file_path.stem, style)

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

    def log_top_lines(self, n: int = 10, msg: str | None = None) -> None:
        msg = f"{msg + '. ' if msg else ''}Top lines of '{self.filename}' ({self.num_lines} lines):"
        logger.info(f"{msg}:\n\n{self.top_lines(n)}")

    def preview_text(self) -> str:
        return WHITESPACE_REGEX.sub(' ', self.text)[0:PREVIEW_CHARS]

    def raw_document_link_txt(self, style: str = '', include_alt_link: bool = False) -> Text:
        txt = Text('', style='white' if include_alt_link else ARCHIVE_LINK_COLOR)

        if args.use_epstein_web_links:
            txt.append(self.epstein_web_link(style=style))

            if include_alt_link:
                txt.append(' (').append(self.epsteinify_link(style='white dim', link_txt='epsteinify')).append(')')
        else:
            txt.append(self.epsteinify_link(style=style))

            if include_alt_link:
                txt.append(' (').append(self.epstein_web_link(style='white dim', link_txt='epsteinweb')).append(')')

        return txt

    def regex_repair_text(self, repairs: dict[str | re.Pattern, str], text: str) -> str:
        for k, v in repairs.items():
            if isinstance(k, re.Pattern):
                text = k.sub(v, text)
            else:
                text = text.replace(k, v)

        return text

    def size_str(self) -> str:
        file_size = float(self.file_path.stat().st_size)

        if file_size > MB:
            size_num = file_size / MB
            size_str = 'MB'
        elif file_size > KB:
            size_num = file_size / KB
            size_str = 'kb'
        else:
            size_num = file_size
            size_str = 'bytes'

        return f"{size_num:,.2f} {size_str}"

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
            return collapse_newlines('\n'.join(lines))

    def _set_computed_fields(self) -> None:
        self.length = len(self.text)
        self.lines = self.text.split('\n')
        self.num_lines = len(self.lines)

    @staticmethod
    def diff_files(files: list[str]) -> None:
        if len(files) != 2:
            raise RuntimeError('Need 2 files')

        files = [f if f.endswith('.txt') else f"{f}.txt" for f in files]
        tmpfiles = [Path(f"tmp_{f}") for f in files]
        docs = [Document(DOCS_DIR.joinpath(f)) for f in files]

        for i, doc in enumerate(docs):
            doc.write_clean_text(tmpfiles[i])

        cmd = f"diff {tmpfiles[0]} {tmpfiles[1]}"
        console.print(f"Running '{cmd}'...")
        results = run(cmd, shell=True, capture_output=True, text=True).stdout
        console.print(f"\nDiff results:")
        console.print(f"{results}\n", style='dim', highlight=False)

        console.print(f"Possible suppression with: ")
        console.print(Text('   suppress left: ').append(f"   '{extract_file_id(files[0])}': 'the same as {extract_file_id(files[1])}',", style='cyan'))
        console.print(Text('  suppress right: ').append(f"   '{extract_file_id(files[1])}': 'the same as {extract_file_id(files[0])}',", style='cyan'))

        for f in tmpfiles:
            f.unlink()


@dataclass
class CommunicationDocument(Document):
    author: str | None = field(init=False)
    author_str: str = field(init=False)
    author_style: str = field(init=False)
    author_txt: Text = field(init=False)
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        super().__post_init__()

    def description(self) -> Text:
        txt = super().description()
        txt.append(f", author='").append(self.author_str, style=self.author_style).append("'")
        txt.append(f", timestamp='{self.timestamp}')")
        return txt

    def raw_document_link_txt(self, _style: str = '', include_alt_link: bool = True) -> Text:
        """Overrides super() method to apply style"""
        return super().raw_document_link_txt(self.author_style, include_alt_link=include_alt_link)

    def timestamp_without_seconds(self) -> str:
        return TIMESTAMP_SECONDS_REGEX.sub('', str(self.timestamp))


@dataclass
class SearchResult:
    document: Document
    lines: list[Text]
