import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from subprocess import run
from typing import ClassVar, Sequence, TypeVar

from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import ALL_FILE_CONFIGS, FALLBACK_TIMESTAMP, VI_DAILY_NEWS_ARTICLE
from epstein_files.util.file_cfg import EmailCfg, FileCfg
from epstein_files.util.data import collapse_newlines, date_str, iso_timestamp, listify, patternize
from epstein_files.util.env import args, logger
from epstein_files.util.file_helper import DOCS_DIR, file_stem_for_id, extract_file_id, file_size_str, is_local_extract_file
from epstein_files.util.rich import SYMBOL_STYLE, console, highlighter, key_value_txt, logger, link_text_obj

WHITESPACE_REGEX = re.compile(r"\s{2,}|\t|\n", re.MULTILINE)
HOUSE_OVERSIGHT = HOUSE_OVERSIGHT_PREFIX.replace('_', ' ').strip()
MIN_DOCUMENT_ID = 10477
INFO_INDENT = 2
INFO_PADDING = (0, 0, 0, INFO_INDENT)

CLOSE_PROPERTIES_CHAR = ']'
MAX_EXTRACTED_TIMESTAMPS = 6
MIN_TIMESTAMP = datetime(1991, 1, 1)
MID_TIMESTAMP = datetime(2007, 1, 1)
MAX_TIMESTAMP = datetime(2022, 12, 31)
TRAILING_DATE_REGEX = re.compile(r' ((around|ca\.|roughly) )?\d{4}-\d{2}(-\d{2})?$')
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)

DOC_TYPE_STYLES = {
    DOCUMENT_CLASS: 'grey69',
    EMAIL_CLASS: 'sea_green2',
    JSON_FILE_CLASS: 'sandy_brown',
    MESSENGER_LOG_CLASS: 'cyan',
    OTHER_FILE_CLASS: 'grey69',
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
    """Base class for all Epstein Files documents."""
    file_path: Path
    author: str | None = None
    config: FileCfg | EmailCfg | None = None
    file_id: str = field(init=False)
    filename: str = field(init=False)
    is_duplicate: bool = False
    length: int = field(init=False)
    lines: list[str] = field(init=False)
    num_lines: int = field(init=False)
    text: str = ''
    timestamp: datetime | None = None
    url_slug: str = field(init=False)  # e.g. 'HOUSE_OVERSIGHT_123456

    # Class variable; only used to cycle color of output when using lines_match()
    file_matching_idx: ClassVar[int] = 0

    def __post_init__(self):
        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)
        self.config = ALL_FILE_CONFIGS.get(self.file_id)
        self.is_duplicate = bool(self.config.duplicate_of_id) if self.config else False

        if self.is_local_extract_file():
            self.url_slug = file_stem_for_id(self.file_id)

            if self.document_type() == EMAIL_CLASS and self.config and self.cfg_type() != 'EmailCfg':
                self.config = EmailCfg.from_file_cfg(self.config)
        else:
            self.url_slug = self.file_path.stem

        self._set_computed_fields(text=self.text or self._load_file())
        self._repair()
        self._extract_author()

    # TODO: remove eventually, unecessary
    def cfg_type(self) -> str | None:
        return type(self.config).__name__ if self.config else None

    def date_str(self) -> str | None:
        return date_str(self.timestamp)

    def description(self) -> Text:
        """Mostly for logging. Brackets are left open for subclasses to add stuff."""
        txt = Text('').append(self.url_slug, style='magenta')
        txt.append(f' {self.document_type()}', style=self.document_type_style())

        if self.timestamp:
            txt.append(' (', style=SYMBOL_STYLE)
            txt.append(f"{iso_timestamp(self.timestamp)}", style=TIMESTAMP_DIM).append(')', style=SYMBOL_STYLE)

        txt.append(" [").append(key_value_txt('num_lines', Text(f"{self.num_lines}", style='cyan')))
        txt.append(', ').append(key_value_txt('size', Text(self.file_size_str(), style='aquamarine1')))
        return txt

    def description_panel(self, include_hints: bool = False) -> Panel:
        """Panelized description() with info_txt(), used in search results."""
        hints = [Text('', style='italic').append(h) for h in (self.hints() if include_hints else [])]
        return Panel(Group(*([self.description()] + hints)), border_style=self.document_type_style(), expand=False)

    def document_type(self) -> str:
        """Annoying workaround for circular import issues and isinstance()."""
        return str(type(self).__name__)

    def document_type_style(self) -> str:
        return DOC_TYPE_STYLES[self.document_type()]

    def duplicate_file_txt(self) -> Text:
        """If the file is a dupe make a nice message to explain what file it's a duplicate of."""
        if not self.config or not self.config.duplicate_of_id:
            raise RuntimeError(f"duplicate_file_txt() called on {self.description()} but not a dupe! config:\n\n{self.config}")

        txt = Text(f"Not showing ", style='white dim italic').append(epstein_media_doc_link_txt(self.file_id, style='cyan'))
        txt.append(f" because it's {self.config.duplicate_reason()} ")
        return txt.append(epstein_media_doc_link_txt(self.config.duplicate_of_id, style='royal_blue1'))

    def epsteinify_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        """Create a Text obj link to this document on epsteinify.com."""
        return link_text_obj(epsteinify_doc_url(self.url_slug), link_txt or self.url_slug, style)

    def epstein_media_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        """Create a Text obj link to this document on epstein.media."""
        return link_text_obj(epstein_media_doc_url(self.url_slug), link_txt or self.url_slug, style)

    def epstein_web_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        """Create a Text obj link to this document on EpsteinWeb."""
        return link_text_obj(epstein_web_doc_url(self.url_slug), link_txt or self.url_slug, style)

    def file_info_panel(self) -> Group:
        """Panel with filename linking to raw file plus any hints/info about the file."""
        panel = Panel(self.raw_document_link_txt(include_alt_link=True), border_style=self._border_style(), expand=False)
        hints = [Padding(hint, INFO_PADDING) for hint in self.hints()]
        return Group(*([panel] + hints))

    def file_size_str(self) -> str:
        return file_size_str(self.file_path)

    def hints(self) -> list[Text]:
        """Additional info about the Document (author, description, and so on) to be desplayed in doc header."""
        hints = listify(self.info_txt())
        hint_msg = self.config.description if self.config else None

        if self.document_type() == OTHER_FILE_CLASS:
            if not hint_msg and VI_DAILY_NEWS_REGEX.search(self.text):
                hint_msg = VI_DAILY_NEWS_ARTICLE
        elif hint_msg:
            hint_msg = f"({hint_msg})"

        if hint_msg:
            hint_msg = TRAILING_DATE_REGEX.sub('', hint_msg)  # a lot of configured file infos have trailing ISO date
            hints.append(highlighter(Text(hint_msg, style='white dim italic')))

        return hints

    def info_txt(self) -> Text | None:
        """Secondary info about this file (recipients, level of certainty, etc). Overload in subclasses."""
        return None

    def is_local_extract_file(self) -> bool:
        """True if file created by extracting text from a court doc (identifiable from filename e.g. HOUSE_OVERSIGHT_012345_1.txt)."""
        return is_local_extract_file(self.filename)

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

    def log_top_lines(self, n: int = 10, msg: str = '', level: int = logging.INFO) -> None:
        """Log first 'n' lines of self.text at 'level'. 'msg' can be optionally provided."""
        separator = '\n\n' if '\n' in msg else '. '
        msg = f"{msg + separator if msg else ''}Top lines of '{self.filename}' ({self.num_lines} lines):"
        logger.log(level, f"{msg}\n\n{self.top_lines(n)}\n")

    def raw_document_link_txt(self, style: str = '', include_alt_link: bool = False) -> Text:
        """Returns colored links to epsteinify and and epsteinweb in a Text object."""
        txt = Text('', style='white' if include_alt_link else ARCHIVE_LINK_COLOR)

        if args.use_epstein_web_links:
            txt.append(self.epstein_web_link(style=style))

            if include_alt_link:
                txt.append(' (').append(self.epstein_media_link(style='white dim', link_txt=EPSTEIN_MEDIA)).append(')')
        else:
            txt.append(self.epstein_media_link(style=style))

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
        """Should be overloaded in subclasses."""
        return 'white'

    def _extract_author(self) -> None:
        if self.config and self.config.author:
            self.author = self.config.author

    def _extract_timestamp(self) -> datetime:
        raise NotImplementedError(f"Should be implemented in subclasses!")

    def _load_file(self):
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        with open(self.file_path) as f:
            text = f.read()
            text = text[1:] if (len(text) > 0 and text[0] == '\ufeff') else text  # remove BOM
            text = self.regex_repair_text(OCR_REPAIRS, text.strip())
            lines = [l.strip() for l in text.split('\n') if not l.startswith(HOUSE_OVERSIGHT)]
            lines = lines[1:] if (len(lines) > 1 and lines[0] == '>>') else lines
            return collapse_newlines('\n'.join(lines))

    def _repair(self) -> None:
        """Can optionally be overloaded in subclasses."""
        pass

    def _set_computed_fields(self, lines: list[str] | None = None, text: str | None = None) -> None:
        if (lines and text):
            raise RuntimeError(f"[{self.filename}] Either 'lines' or 'text' arg must be provided (got both)")
        elif lines is not None:
            self.lines = lines
            self.text = '\n'.join(lines)
        elif text is not None:
            self.lines = text.split('\n')
            self.text = text
        else:
            raise RuntimeError(f"[{self.filename}] Either 'lines' or 'text' arg must be provided (neither was)")

        self.length = len(self.text)
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

        files = [f"{HOUSE_OVERSIGHT_PREFIX}{f}" if len(f) == 6 else f for f in files]
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
    def sort_by_timestamp(docs: Sequence['DocumentType']) -> list['DocumentType']:
        return sorted(docs, key=lambda doc: [doc.timestamp or FALLBACK_TIMESTAMP, doc.file_id])

    @classmethod
    def uniquify(cls, documents: Sequence['DocumentType']) -> Sequence['DocumentType']:
        """Uniquify by file_id."""
        id_map = {doc.file_id: doc for doc in documents}
        return [doc for doc in id_map.values()]


DocumentType = TypeVar('DocumentType', bound=Document)


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
