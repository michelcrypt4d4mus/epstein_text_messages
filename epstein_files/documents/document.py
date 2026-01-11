import logging
import re
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from subprocess import run
from typing import Callable, ClassVar, Sequence, TypeVar

from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import ALL_FILE_CONFIGS, FALLBACK_TIMESTAMP
from epstein_files.util.data import collapse_newlines, date_str, patternize, remove_zero_time_from_timestamp_str, without_falsey
from epstein_files.util.doc_cfg import DUPE_TYPE_STRS, EmailCfg, DocCfg, Metadata, TextCfg
from epstein_files.util.env import DOCS_DIR, args
from epstein_files.util.file_helper import extract_file_id, file_size, file_size_str, file_size_to_str, is_local_extract_file
from epstein_files.util.logging import DOC_TYPE_STYLES, FILENAME_STYLE, logger
from epstein_files.util.rich import INFO_STYLE, NA_TXT, SYMBOL_STYLE, add_cols_to_table, build_table, console, highlighter, join_texts, key_value_txt, link_text_obj, parenthesize
from epstein_files.util.search_result import MatchedLine

ALT_LINK_STYLE = 'white dim'
CLOSE_PROPERTIES_CHAR = ']'
HOUSE_OVERSIGHT = HOUSE_OVERSIGHT_PREFIX.replace('_', ' ').strip()
INFO_INDENT = 2
INFO_PADDING = (0, 0, 0, INFO_INDENT)
MAX_TOP_LINES_LEN = 4000  # Only for logging
MIN_DOCUMENT_ID = 10477
WHITESPACE_REGEX = re.compile(r"\s{2,}|\t|\n", re.MULTILINE)

MIN_TIMESTAMP = datetime(1991, 1, 1)
MID_TIMESTAMP = datetime(2007, 1, 1)
MAX_TIMESTAMP = datetime(2020, 1, 1)

FILENAME_MATCH_STYLES = [
    'dark_green',
    'green',
    'spring_green4',
]

METADATA_FIELDS = [
    'author',
    'file_id',
    'timestamp'
]

OCR_REPAIRS = {
    re.compile(r'\.corn\b'): '.com',
    re.compile('ln(adequate|dyke)'): r'In\1',
    'Nil Priell': 'Nili Priell',
}

SUMMARY_TABLE_COLS: list[str | dict] = [
    'Count',
    {'name': 'Has Author', 'style': 'honeydew2'},
    {'name': 'No Author', 'style': 'wheat4'},
    {'name': 'Size', 'justify': 'right', 'style': 'dim'},
]


@dataclass
class Document:
    """
    Base class for all Epstein Files documents.

    Attributes:
        file_path (Path): Local path to file
        author (Name): Who is responsible for the text in the file
        config (DocCfg): Information about this fil
        file_id (str): 6 digit (or 8 digits if it's a local extract file) string ID
        filename (str): File's basename
        lines (str): Number of lines in the file after all the cleanup
        text (str): Contents of the file
        timestamp (datetime | None): When the file was originally created
        url_slug (str): Version of the filename that works in links to epsteinify etc.
    """
    file_path: Path
    # Optional fields
    author: Name = None
    config: EmailCfg | DocCfg | TextCfg | None = None
    file_id: str = field(init=False)
    filename: str = field(init=False)
    lines: list[str] = field(default_factory=list)
    text: str = ''
    timestamp: datetime | None = None
    url_slug: str = ''

    # Class variables
    include_description_in_summary_panel: ClassVar[bool] = False
    strip_whitespace: ClassVar[bool] = True  # Overridden in JsonFile

    def __post_init__(self):
        if not self.file_path.exists():
            raise FileNotFoundError(f"File '{self.file_path.name}' does not exist!")

        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)
        # config and url_slug could have been pre-set in Email
        self.config = self.config or deepcopy(ALL_FILE_CONFIGS.get(self.file_id))
        self.url_slug = self.url_slug or self.filename.split('.')[0]

        if not self.text:
            self._load_file()

        self._repair()
        self._extract_author()
        self.timestamp = self._extract_timestamp()

    def config_description(self) -> str | None:
        """Overloaded in OtherFile."""
        if self.config and self.config.description:
            return f"({self.config.description})"

    def date_str(self) -> str | None:
        return date_str(self.timestamp)

    def duplicate_file_txt(self) -> Text:
        """If the file is a dupe make a nice message to explain what file it's a duplicate of."""
        if not self.is_duplicate():
            raise RuntimeError(f"duplicate_file_txt() called on {self.summary()} but not a dupe! config:\n\n{self.config}")

        txt = Text(f"Not showing ", style=INFO_STYLE).append(epstein_media_doc_link_txt(self.file_id, style='cyan'))
        txt.append(f" because it's {DUPE_TYPE_STRS[self.config.dupe_type]} ")
        return txt.append(epstein_media_doc_link_txt(self.config.duplicate_of_id, style='royal_blue1'))

    def duplicate_of_id(self) -> str | None:
        if self.config and self.config.duplicate_of_id:
            return self.config.duplicate_of_id

    def epsteinify_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        return self.external_link(epsteinify_doc_url, style, link_txt)

    def epstein_media_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        return self.external_link(epstein_media_doc_url, style, link_txt)

    def epstein_web_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        return self.external_link(epstein_web_doc_url, style, link_txt)

    def rollcall_link(self, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        return self.external_link(rollcall_doc_url, style, link_txt)

    def external_link(self, fxn: Callable[[str], str], style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
        return link_text_obj(fxn(self.url_slug), link_txt or self.file_path.stem, style)

    def external_links_txt(self, style: str = '', include_alt_links: bool = False) -> Text:
        """Returns colored links to epstein.media and alternates in a Text object."""
        links = [self.epstein_media_link(style=style)]

        if include_alt_links:
            links.append(self.epsteinify_link(style=ALT_LINK_STYLE, link_txt=EPSTEINIFY))
            links.append(self.epstein_web_link(style=ALT_LINK_STYLE, link_txt=EPSTEIN_WEB))

            if self._class_name() == 'Email':
                links.append(self.rollcall_link(style=ALT_LINK_STYLE, link_txt=ROLLCALL))

        links = [links[0]] + [parenthesize(link) for link in links[1:]]
        base_txt = Text('', style='white' if include_alt_links else ARCHIVE_LINK_COLOR)
        return base_txt.append(join_texts(links))

    def file_id_debug_info(self) -> str:
        return ', '.join([f"{prop}={getattr(self, prop)}" for prop in ['file_id', 'filename', 'url_slug']])

    def file_info_panel(self) -> Group:
        """Panel with filename linking to raw file plus any additional info about the file."""
        panel = Panel(self.external_links_txt(include_alt_links=True), border_style=self._border_style(), expand=False)
        padded_info = [Padding(sentence, INFO_PADDING) for sentence in self.info()]
        return Group(*([panel] + padded_info))

    def file_size(self) -> int:
        return file_size(self.file_path)

    def file_size_str(self, decimal_places: int | None = None) -> str:
        return file_size_str(self.file_path, decimal_places)

    def info(self) -> list[Text]:
        """0 to 2 sentences containing the info_txt() as well as any configured description."""
        return without_falsey([
            self.info_txt(),
            highlighter(Text(self.config_description(), style=INFO_STYLE)) if self.config_description() else None
        ])

    def info_txt(self) -> Text | None:
        """Secondary info about this file (description recipients, etc). Overload in subclasses."""
        return None

    def is_duplicate(self) -> bool:
        return bool(self.duplicate_of_id())

    def is_local_extract_file(self) -> bool:
        """True if extracted from other file (identifiable from filename e.g. HOUSE_OVERSIGHT_012345_1.txt)."""
        return is_local_extract_file(self.filename)

    def length(self) -> int:
        return len(self.text)

    def log(self, msg: str, level: int = logging.INFO):
        """Log with filename as a prefix."""
        logger.log(level, f"{self.file_path.stem} {msg}")

    def log_top_lines(self, n: int = 10, msg: str = '', level: int = logging.INFO) -> None:
        """Log first 'n' lines of self.text at 'level'. 'msg' can be optionally provided."""
        separator = '\n\n' if '\n' in msg else '. '
        msg = (msg + separator) if msg else ''
        self.log(f"{msg}First {n} lines:\n\n{self.top_lines(n)}\n", level)

    def matching_lines(self, _pattern: re.Pattern | str) -> list[MatchedLine]:
        """Return lines matching a regex as colored list[Text]."""
        pattern = patternize(_pattern)
        return [MatchedLine(line, i) for i, line in enumerate(self.lines) if pattern.search(line)]

    def metadata(self) -> Metadata:
        metadata = self.config.metadata() if self.config else {}
        metadata.update({k: v for k, v in asdict(self).items() if k in METADATA_FIELDS and v is not None})
        metadata['bytes'] = self.file_size()
        metadata['filename'] = f"{self.url_slug}.txt"
        metadata['num_lines'] = self.num_lines()
        metadata['type'] = self._class_name()

        if self.is_local_extract_file():
            metadata['extracted_file'] = {
                'explanation': 'manually extracted from one of the other files',
                'extracted_from': self.url_slug + '.txt',
                'url': extracted_file_url(self.filename),
            }

        return metadata

    def num_lines(self) -> int:
        return len(self.lines)

    def raw_text(self) -> str:
        with open(self.file_path) as f:
            return f.read()

    def repair_ocr_text(self, repairs: dict[str | re.Pattern, str], text: str) -> str:
        """Apply a dict of repairs (key is pattern or string, value is replacement string) to text."""
        for k, v in repairs.items():
            if isinstance(k, re.Pattern):
                text = k.sub(v, text)
            else:
                text = text.replace(k, v)

        return text

    def sort_key(self) -> tuple[datetime, str, int]:
        """Sort by timestamp, file_id, then whether or not it's a duplicate file."""
        if self.is_duplicate():
            sort_id = self.config.duplicate_of_id
            dupe_idx = 1
        else:
            sort_id = self.file_id
            dupe_idx = 0

        return (self.timestamp or FALLBACK_TIMESTAMP, sort_id, dupe_idx)

    def source_file_id(self) -> str:
        """Strip off the _1, _2, etc. suffixes for extracted documents."""
        return self.file_id[0:6]

    def summary(self) -> Text:
        """Summary of this file for logging. Brackets are left open for subclasses to add stuff."""
        txt = Text('').append(self._class_name(), style=self._class_style())
        txt.append(f" {self.file_path.stem}", style=FILENAME_STYLE)

        if self.timestamp:
            timestamp_str = remove_zero_time_from_timestamp_str(self.timestamp).replace('T', ' ')
            txt.append(' (', style=SYMBOL_STYLE)
            txt.append(f"{timestamp_str}", style=TIMESTAMP_DIM).append(')', style=SYMBOL_STYLE)

        txt.append(' [').append(key_value_txt('size', Text(self.file_size_str(0), style='aquamarine1')))
        txt.append(", ").append(key_value_txt('lines', self.num_lines()))

        if self.config and self.config.duplicate_of_id:
            txt.append(", ").append(key_value_txt('dupe_of', Text(self.config.duplicate_of_id, style='magenta')))

        return txt

    def summary_panel(self) -> Panel:
        """Panelized description() with info_txt(), used in search results."""
        sentences = [self.summary()]

        if self.include_description_in_summary_panel:
            sentences += [Text('', style='italic').append(h) for h in self.info()]

        return Panel(Group(*sentences), border_style=self._class_style(), expand=False)

    def top_lines(self, n: int = 10) -> str:
        """First n lines."""
        return '\n'.join(self.lines[0:n])[:MAX_TOP_LINES_LEN]

    def warn(self, msg: str) -> None:
        self.log(msg, level=logging.WARNING)

    def _border_style(self) -> str:
        """Should be overloaded in subclasses."""
        return 'white'

    def _class_name(self) -> str:
        """Annoying workaround for circular import issues and isinstance()."""
        return str(type(self).__name__)

    def _class_style(self) -> str:
        return DOC_TYPE_STYLES[self._class_name()]

    def _extract_author(self) -> None:
        """Get author from config. Extended in Email subclass to also check headers."""
        if self.config and self.config.author:
            self.author = self.config.author

    def _extract_timestamp(self) -> datetime | None:
        """Should be implemented in subclasses."""
        pass

    def _load_file(self) -> None:
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        text = self.raw_text()
        text = text[1:] if (len(text) > 0 and text[0] == '\ufeff') else text  # remove BOM
        text = self.repair_ocr_text(OCR_REPAIRS, text.strip())

        lines = [
            line.strip() if self.strip_whitespace else line for line in text.split('\n')
            if not line.startswith(HOUSE_OVERSIGHT)
        ]

        self.text = collapse_newlines('\n'.join(lines))
        self.lines = self.text.split('\n')

    def _repair(self) -> None:
        """Can optionally be overloaded in subclasses to further improve self.text."""
        pass

    def _set_computed_fields(self, lines: list[str] | None = None, text: str | None = None) -> None:
        """Sets all fields derived from self.text based on either 'lines' or 'text' arg."""
        if (lines and text):
            raise RuntimeError(f"[{self.filename}] Either 'lines' or 'text' arg must be provided (got both)")
        elif lines is not None:
            self.text = '\n'.join(lines).strip()
        elif text is not None:
            self.text = text.strip()
        else:
            raise RuntimeError(f"[{self.filename}] Either 'lines' or 'text' arg must be provided (neither was)")

        self.lines = [line.strip() if self.strip_whitespace else line for line in self.text.split('\n')]

    def _write_clean_text(self, output_path: Path) -> None:
        """Write self.text to 'output_path'. Used only for diffing files."""
        if output_path.exists():
            if str(output_path.name).startswith(HOUSE_OVERSIGHT_PREFIX):
                raise RuntimeError(f"'{output_path}' already exists! Not overwriting.")
            else:
                logger.warning(f"Overwriting '{output_path}'...")

        with open(output_path, 'w') as f:
            f.write(self.text)

        logger.warning(f"Wrote {self.length()} chars of cleaned {self.filename} to {output_path}.")

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield self.file_info_panel()
        text_panel = Panel(highlighter(self.text), border_style=self._border_style(), expand=False)
        yield Padding(text_panel, (0, 0, 1, INFO_INDENT))

    def __str__(self) -> str:
        return self.summary().plain

    @classmethod
    def file_info_table(cls, title: str, first_col_name: str) -> Table:
        """Empty table with appropriate cols for summarizing groups of files."""
        table = build_table(title)
        cols = [{'name': first_col_name, 'min_width': 14}] + SUMMARY_TABLE_COLS
        add_cols_to_table(table, cols, 'right')
        return table

    @classmethod
    def files_info(cls, files: Sequence['Document'], is_author_na: bool = False) -> dict[str, str | Text]:
        """Summary info about a group of files."""
        file_count = len(files)
        author_count = cls.known_author_count(files)

        return {
            'count': str(file_count),
            'author_count': NA_TXT if is_author_na else str(author_count),
            'no_author_count': NA_TXT if is_author_na else str(file_count - author_count),
            'bytes': file_size_to_str(sum([f.file_size() for f in files])),
        }

    @classmethod
    def files_info_row(cls, files: Sequence['Document'], author_na: bool = False) -> Sequence[str | Text]:
        return [v for v in cls.files_info(files, author_na).values()]

    @staticmethod
    def diff_files(files: list[str]) -> None:
        """Diff the contents of two Documents after all cleanup, BOM removal, etc."""
        if len(files) != 2:
            raise RuntimeError('Need 2 files')
        elif files[0] == files[1]:
            raise RuntimeError(f"Filenames are the same!")

        files = [f"{HOUSE_OVERSIGHT_PREFIX}{f}" if len(f) == 6 else f for f in files]
        files = [f if f.endswith('.txt') else f"{f}.txt" for f in files]
        tmpfiles = [Path(f"tmp_{f}") for f in files]
        docs = [Document(DOCS_DIR.joinpath(f)) for f in files]

        for i, doc in enumerate(docs):
            doc._write_clean_text(tmpfiles[i])

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
    def known_author_count(docs: Sequence['Document']) -> int:
        """Count of how many Document objects have an author attribution."""
        return len([doc for doc in docs if doc.author])

    @staticmethod
    def sort_by_timestamp(docs: Sequence['DocumentType']) -> list['DocumentType']:
        return sorted(docs, key=lambda doc: doc.sort_key())

    @staticmethod
    def uniquify(documents: Sequence['DocumentType']) -> Sequence['DocumentType']:
        """Uniquify by file_id."""
        id_map = {doc.file_id: doc for doc in documents}
        return [doc for doc in id_map.values()]

    @staticmethod
    def without_dupes(docs: Sequence['DocumentType']) -> list['DocumentType']:
        return [doc for doc in docs if not doc.is_duplicate()]


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
