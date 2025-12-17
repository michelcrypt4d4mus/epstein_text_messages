import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from subprocess import run
from typing import ClassVar

from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import ARCHIVE_LINK_COLOR, EPSTEINIFY, EPSTEIN_WEB, epsteinify_doc_url, epstein_web_doc_url
from epstein_files.util.constants import FILE_DESCRIPTIONS
from epstein_files.util.data import collapse_newlines, escape_single_quotes, patternize
from epstein_files.util.env import args, logger
from epstein_files.util.file_helper import DOCS_DIR, build_filename_for_id, extract_file_id, file_size_str, is_local_extract_file
from epstein_files.util.rich import console, highlighter, logger, link_text_obj

TIMESTAMP_SECONDS_REGEX = re.compile(r":\d{2}$")
WHITESPACE_REGEX = re.compile(r"\s{2,}|\t|\n", re.MULTILINE)
HOUSE_OVERSIGHT = HOUSE_OVERSIGHT_PREFIX.replace('_', ' ').strip()
MIN_DOCUMENT_ID = 10477
PREVIEW_CHARS = 520
INFO_INDENT = 2
INFO_PADDING = (0, 0, 0, INFO_INDENT)

DOC_TYPE_STYLES = {
    DOCUMENT_CLASS: 'grey69',
    EMAIL_CLASS: 'sea_green2',
    MESSENGER_LOG_CLASS: 'cyan',
}

OCR_REPAIRS = {
    re.compile(r'\.corn\b'): '.com',
    re.compile('ln(adequate|dyke)'): r'In\1',
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
    file_id: str = field(init=False)
    filename: str = field(init=False)
    length: int = field(init=False)
    lines: list[str] = field(init=False)
    num_lines: int = field(init=False)
    text: str = ''
    url_slug: str = field(init=False)  # e.g. 'HOUSE_OVERSIGHT_123456

    # Class variable; only used to cycle color of output when using lines_match()
    file_matching_idx: ClassVar[int] = 0

    def __post_init__(self):
        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)

        if is_local_extract_file(self.filename):
            self.url_slug = build_filename_for_id(self.file_id)
        else:
            self.url_slug = self.file_path.stem

        self.text = self.text or self._load_file()
        self._set_computed_fields()

    def description(self) -> Text:
        """Mostly for logging."""
        doc_type = str(type(self).__name__)
        txt = Text('').append(self.file_path.stem, style='magenta')
        txt.append(f' {doc_type} ', style=self.document_type_style())
        txt.append(f"(num_lines=").append(f"{self.num_lines}", style='cyan')
        txt.append(", size=").append(file_size_str(self.file_path), style='aquamarine1')
        return txt.append(')') if doc_type == DOCUMENT_CLASS else txt

    def description_panel(self, include_hints: bool = True) -> Panel:
        """Panelized description() with info_txt(), used in search results."""
        hints = [Text('', style='italic').append(h) for h in (self.hints() if include_hints else [])]
        return Panel(Group(*([self.description()] + hints)), border_style=self.document_type_style(), expand=False)

    def document_type_style(self) -> str:
        return DOC_TYPE_STYLES[str(type(self).__name__)]

    def epsteinify_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        """Create a Text obj link to this document on epsteinify.com."""
        return link_text_obj(epsteinify_doc_url(self.url_slug), link_txt or self.file_path.stem, style)

    def epstein_web_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        """Create a Text obj link to this document on EpsteinWeb."""
        return link_text_obj(epstein_web_doc_url(self.url_slug), link_txt or self.file_path.stem, style)

    def file_info_panel(self) -> Group:
        """Panel with filename linking to raw file plus any hints/info about the file."""
        panel = Panel(self.raw_document_link_txt(include_alt_link=True), border_style=self._border_style(), expand=False)
        hints = [Padding(hint, INFO_PADDING) for hint in self.hints()]
        return Group(*([panel] + hints))

    def highlighted_preview_text(self) -> Text:
        try:
            return highlighter(escape(self.preview_text()))
        except Exception as e:
            logger.error(f"Failed to apply markup in string '{escape_single_quotes(self.preview_text())}'\n"
                         f"Original string: '{escape_single_quotes(self.preview_text())}'\n"
                         f"File: '{self.filename}'\n")

            return Text(escape(self.preview_text()))

    def hints(self) -> list[Text]:
        """Additional info about the Document (author, FILE_DESCRIPTIONS value, and so on)."""
        file_info = self.info_txt()
        hints = [file_info] if file_info else []
        hints += [Text(f"({FILE_DESCRIPTIONS[self.file_id]})", style='gray30')] if self.file_id in FILE_DESCRIPTIONS else []
        return hints

    def info_txt(self) -> Text | None:
        """Secondary info about this file (recipients, level of certainty, etc). Overload in subclasses."""
        return None

    def lines_matching_txt(self, _pattern: re.Pattern | str) -> list[Text]:
        pattern = patternize(_pattern)
        matched_lines = [line for line in self.lines if pattern.search(line)]

        if len(matched_lines) == 0:
            return []

        file_style = FILENAME_MATCH_STYLES[type(self).file_matching_idx % len(FILENAME_MATCH_STYLES)]
        type(self).file_matching_idx += 1

        return [
            Text('').append(self.file_path.name, style=file_style).append(':').append(line)
            for line in matched_lines
        ]

    def log_top_lines(self, n: int = 10, msg: str | None = None) -> None:
        msg = f"{msg + '. ' if msg else ''}Top lines of '{self.filename}' ({self.num_lines} lines):"
        logger.info(f"{msg}:\n\n{self.top_lines(n)}")

    def preview_text(self) -> str:
        return WHITESPACE_REGEX.sub(' ', self.text)[0:PREVIEW_CHARS]

    def raw_document_link_txt(self, style: str = '', include_alt_link: bool = False) -> Text:
        """Returns colored links to epsteinify and and epsteinweb in a Text object."""
        txt = Text('', style='white' if include_alt_link else ARCHIVE_LINK_COLOR)

        if args.use_epstein_web_links:
            txt.append(self.epstein_web_link(style=style))

            if include_alt_link:
                txt.append(' (').append(self.epsteinify_link(style='white dim', link_txt=EPSTEINIFY)).append(')')
        else:
            txt.append(self.epsteinify_link(style=style))

            if include_alt_link:
                txt.append(' (').append(self.epstein_web_link(style='white dim', link_txt=EPSTEIN_WEB)).append(')')

        return txt

    def regex_repair_text(self, repairs: dict[str | re.Pattern, str], text: str) -> str:
        """Apply a dict of repairs (key is pattern or string, value is replacement string) to text."""
        for k, v in repairs.items():
            if isinstance(k, re.Pattern):
                text = k.sub(v, text)
            else:
                text = text.replace(k, v)

        return text

    def top_lines(self, n: int = 10) -> str:
        return '\n'.join(self.lines[0:n])

    def write_clean_text(self, output_path: Path) -> None:
        """Write self.text to 'output_path'."""
        if output_path.exists():
            if str(output_path.name).startswith(HOUSE_OVERSIGHT_PREFIX):
                raise RuntimeError(f"'{output_path}' already exists! Not overwriting.")
            else:
                logger.warning(f"Overwriting '{output_path}'...")

        with open(output_path, 'w') as f:
            f.write(self.text)

        logger.warning(f"Wrote {self.length} chars of cleaned {self.filename} to {output_path}.")

    def _border_style(self) -> str:
        """Should be implemented in subclasses."""
        return 'white'

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

    def __rich_console__(self, _console: Console, _options: ConsoleOptions) -> RenderResult:
        yield self.file_info_panel()
        text_panel = Panel(highlighter(self.text), border_style=self._border_style(), expand=False)
        yield Padding(text_panel, (0, 0, 1, INFO_INDENT))

    def __str__(self) -> str:
        return self.description().plain

    @staticmethod
    def diff_files(files: list[str]) -> None:
        if len(files) != 2:
            raise RuntimeError('Need 2 files')
        elif files[0] == files[1]:
            raise RuntimeError(f"Filenames are the same!")

        files = [f if f.endswith('.txt') else f"{f}.txt" for f in files]
        tmpfiles = [Path(f"tmp_{f}") for f in files]
        docs = [Document(DOCS_DIR.joinpath(f)) for f in files]

        for i, doc in enumerate(docs):
            doc.write_clean_text(tmpfiles[i])

        cmd = f"diff {tmpfiles[0]} {tmpfiles[1]}"
        console.print(f"Running '{cmd}'...")
        results = run(cmd, shell=True, capture_output=True, text=True).stdout

        for line in _color_diff_output(results):
            console.print(line, highlight=True)

        console.print(f"Possible suppression with: ")
        console.print(Text('   suppress left: ').append(f"   '{extract_file_id(files[0])}': 'the same as {extract_file_id(files[1])}',", style='cyan'))
        console.print(Text('  suppress right: ').append(f"   '{extract_file_id(files[1])}': 'the same as {extract_file_id(files[0])}',", style='cyan'))

        for f in tmpfiles:
            f.unlink()

    @staticmethod
    def uniquify(documents: list['Document']) -> list['Document']:
        """Uniquify by file_id."""
        id_map = {doc.file_id: doc for doc in documents}
        return [doc for doc in id_map.values()]


@dataclass
class CommunicationDocument(Document):
    """Superclass for Email and MessengerLog."""
    author: str | None = None
    author_str: str = field(init=False)
    author_style: str = field(init=False)
    author_txt: Text = field(init=False)
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self._repair()
        self._extract_author()
        self.author_txt = Text(self.author_str, style=self.author_style)
        self.timestamp = self._extract_timestamp()

    def author_or_unknown(self) -> str:
        return self.author or UNKNOWN

    def description(self) -> Text:
        """One line summary mostly for logging."""
        txt = super().description()
        txt.append(f", timestamp=").append(str(self.timestamp), style='dim dark_cyan')
        txt.append(f", author=").append(self.author_str, style=self.author_style)
        return txt.append(')')

    def raw_document_link_txt(self, _style: str = '', include_alt_link: bool = True) -> Text:
        """Overrides super() method to apply author_style."""
        return super().raw_document_link_txt(self.author_style, include_alt_link=include_alt_link)

    def timestamp_without_seconds(self) -> str:
        return TIMESTAMP_SECONDS_REGEX.sub('', str(self.timestamp))

    def _extract_author(self) -> None:
        raise NotImplementedError(f"Should be implemented in subclasses!")

    def _extract_timestamp(self) -> datetime:
        raise NotImplementedError(f"Should be implemented in subclasses!")

    def _repair(self) -> None:
        """Can optionally be overloaded in subclasses."""
        pass


@dataclass
class SearchResult:
    document: Document
    lines: list[Text]

    def unprefixed_lines(self) -> list[str]:
        return [line.plain.split(':', 1)[1] for line in self.lines]


def _color_diff_output(diff_result: str) -> list[Text]:
    txts = [Text('diff output:')]
    style = 'dim'

    for line in diff_result.split('\n'):
        if line.startswith('>'):
            style='spring_green4'
        elif line.startswith('<'):
            style='sea_green1'

        txts.append(Text(line, style=style))

    return txts
