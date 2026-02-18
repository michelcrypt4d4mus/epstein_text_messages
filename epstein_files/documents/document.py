import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import ClassVar, Self, Sequence, TypeVar

from inflection import underscore
from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from epstein_files.documents.documents.doc_cfg import DUPE_TYPE_STRS, DebugDict, EmailCfg, DocCfg, Metadata
from epstein_files.documents.documents.file_info import FileInfo
from epstein_files.documents.documents.search_result import MatchedLine
from epstein_files.documents.emails.constants import DOJ_EMAIL_OCR_REPAIRS, FALLBACK_TIMESTAMP
from epstein_files.documents.emails.email_header import DETECT_EMAIL_REGEX
from epstein_files.output.highlight_config import get_style_for_name
from epstein_files.output.rich import (INFO_STYLE, NA_TXT, SKIPPED_FILE_MSG_PADDING, SYMBOL_STYLE,
     add_cols_to_table, build_table, console, highlighter, styled_key_value, prefix_with, styled_dict,
     wrap_in_markup_style)
from epstein_files.output.sites import EXTRACTS_BASE_URL
from epstein_files.people.interesting_people import UNINTERESTING_AUTHORS
from epstein_files.util.constant.names import Name
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import epstein_media_doc_link_txt
from epstein_files.util.constants import CONFIGS_BY_ID, MAX_CHARS_TO_PRINT
from epstein_files.util.helpers.data_helpers import (collapse_newlines, date_str, patternize, prefix_keys,
     remove_zero_time, without_falsey)
from epstein_files.util.helpers.file_helper import coerce_file_path, file_size_to_str
from epstein_files.util.helpers.string_helper import join_truthy
from epstein_files.util.logging import DOC_TYPE_STYLES, FILENAME_STYLE, logger

CHECK_LINK_FOR_DETAILS = 'not shown here, check original PDF for details'
CLOSE_PROPERTIES_CHAR = ']'
HOUSE_OVERSIGHT = HOUSE_OVERSIGHT_PREFIX.replace('_', ' ').strip()
WHITESPACE_REGEX = re.compile(r"\s{2,}|\t|\n", re.MULTILINE)

INFO_INDENT = 2
INFO_PADDING = (0, 0, 0, INFO_INDENT)
MIN_DOCUMENT_ID = 10477

FILENAME_MATCH_STYLES = [
    'dark_green',
    'green',
    'spring_green4',
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
    {'name': 'Uncertain Author', 'style': 'royal_blue1 dim'},
    {'name': 'Size', 'justify': 'right', 'style': 'dim'},
]

DEBUG_PROPS = [
    'is_interesting',
    'num_lines',
    'timestamp',
]

DEBUG_PROPS_TRUTHY_ONLY = [
    AUTHOR,
    'category',
    'is_empty',
]

METADATA_FIELDS = [
    AUTHOR,
    'file_id',
    'filename',
    'num_lines',
    'timestamp',
]


@dataclass
class Document:
    """
    Base class for all Epstein Files documents.

    Attributes:
        file_path (Path): Local path to file
        author (Name): Writer of the text in the file
        file_info (FileInfo): Manages things having to do with the underlying file (paths, URLs, etc.)
        lines (list[str]): Number of lines in the file after all the cleanup
        text (str): Contents of the file
        timestamp (datetime, optional): When the file was originally created
    """
    file_path: Path

    # Optional and/or derived at instantiation time
    author: Name = None
    file_info: FileInfo = field(init=False)
    lines: list[str] = field(default_factory=list)
    text: str = ''
    timestamp: datetime | None = None

    # Class constants
    INCLUDE_DESCRIPTION_IN_SUMMARY_PANEL: ClassVar[bool] = False
    STRIP_WHITESPACE: ClassVar[bool] = True  # Overridden in JsonFile

    @property
    def border_style(self) -> str:
        """Should be overloaded in subclasses."""
        return 'white'

    @property
    def category(self) -> str:
        return self.config.category if self.config and self.config.category else self.default_category()

    @property
    def config(self) -> DocCfg | None:
        """Get the configured `DocCfg` object for this file id (if any)."""
        return CONFIGS_BY_ID.get(self.file_id)

    @property
    def config_description(self) -> str:
        """Add parentheses to `self.config.description`."""
        return f"({self.config.description})" if self.config and self.config.description else ''

    @property
    def config_description_txt(self) -> Text | None:
        """Add parentheses to `self.config.description`."""
        return highlighter(Text(self.config_description, style=INFO_STYLE)) if self.config_description else None

    @property
    def config_replace_text_with(self) -> str | None:
        """Configured replacement text."""
        if self.config and self.config.replace_text_with:
            text = join_truthy(self.config.author, self.config.replace_text_with)

            if len(text) < 300:
                return f"(Text of {text} {CHECK_LINK_FOR_DETAILS})"
            else:
                return text

    @property
    def date_str(self) -> str | None:
        return date_str(self.timestamp)

    @property
    def duplicate_file_txt(self) -> Text:
        """If the file is a dupe make a nice message to explain what file it's a duplicate of."""
        if not self.is_duplicate:
            raise RuntimeError(f"duplicate_file_txt() called on {self.summary} but not a dupe! config:\n\n{self.config}")

        txt = Text(f"Not showing ", style=INFO_STYLE).append(epstein_media_doc_link_txt(self.file_id, style='cyan'))
        txt.append(f" because it's {DUPE_TYPE_STRS[self.config.dupe_type]} ")
        return txt.append(epstein_media_doc_link_txt(self.config.duplicate_of_id, style='royal_blue1'))

    @property
    def duplicate_file_txt_padded(self) -> Padding:
        return Padding(self.duplicate_file_txt.append('...'), SKIPPED_FILE_MSG_PADDING)

    @property
    def duplicate_of_id(self) -> str | None:
        if self.config and self.config.duplicate_of_id:
            return self.config.duplicate_of_id

    @property
    def external_link_markup(self) -> str:
        """Rich markup string with link to source document."""
        return self.file_info.external_link_markup(get_style_for_name(self.author) if self.author else '')

    @property
    def file_id(self) -> str:
        return self.file_info.file_id

    @property
    def filename(self) -> str:
        return self.file_info.filename

    @property
    def info(self) -> list[Text]:
        """0 to 2 sentences containing the info_txt() as well as any configured description."""
        return without_falsey([self.subheader, self.config_description_txt])

    @property
    def is_attribution_uncertain(self) -> bool:
        return bool(self.config and self.config.is_attribution_uncertain)

    @property
    def is_duplicate(self) -> bool:
        return bool(self.duplicate_of_id)

    @property
    def is_email(self) -> bool:
        """True if the text looks like it's probably an email."""
        search_area = self.repair_ocr_text(DOJ_EMAIL_OCR_REPAIRS, self.text[0:5000])
        return isinstance(self.config, EmailCfg) or bool(DETECT_EMAIL_REGEX.match(search_area) and self.config is None)

    @property
    def is_empty(self) -> bool:
        return len(self.text.strip()) == 0

    @property
    def is_interesting(self) -> bool | None:
        """
        If `self.config.is_of_interest` returns a bool use that, otherwise house oversight files are
        interesting if they are empty and uninteresting authors are uninteresting.
        Checking of `TEXTERS_OF_INTEREST` etc. is left to the relevant subclass in cases where this
        function returns None.
        """
        if self.config and self.config.is_of_interest is not None:
            return self.config.is_of_interest
        elif self.file_info.is_house_oversight_file and not (self.author or self.config):
            return True
        elif self.author in UNINTERESTING_AUTHORS:
            return False

    @property
    def length(self) -> int:
        return len(self.text)

    @property
    def metadata(self) -> Metadata:
        metadata = self.config.metadata if self.config else {}
        metadata.update({k: getattr(self, k) for k in METADATA_FIELDS if getattr(self, k) is not None})
        metadata['file_size'] = self.file_info.file_size
        metadata['type'] = self._class_name

        if self.file_info.is_local_extract_file:
            metadata['extracted_file'] = {
                'explanation': 'manually extracted from one of the other files',
                'extracted_from': self.file_info.url_slug + '.txt',
                'url': f"{EXTRACTS_BASE_URL}/{self.filename}",
            }

        return metadata

    @property
    def num_lines(self) -> int:
        return len(self.lines)

    @property
    def panel_title_timestamp(self) -> str | None:
        """String placed in the `title` of the enclosing `Panel` when printing this document's text."""
        if (self.timestamp or FALLBACK_TIMESTAMP) == FALLBACK_TIMESTAMP:
            return None

        prefix = '' if self.config and self.config.timestamp else 'inferred '
        return f"{prefix}timestamp: {remove_zero_time(self.timestamp)}"

    @property
    def prettified_text(self) -> Text:
        """Returns the string we want to print as the body of the document."""
        style = INFO_STYLE if self.config_replace_text_with and len(self.config_replace_text_with) < 300 else ''
        text = self.config_replace_text_with or self.text
        trim_footer_txt = None

        if self.config and self.config.truncate_to:
            txt = highlighter(Text(text[0:self.config.truncate_to], style))
            trim_footer_txt = self.truncation_note(self.config.truncate_to)
            return txt.append('...\n\n').append(trim_footer_txt)
        else:
            return highlighter(Text(text, style))

    @property
    def subheader(self) -> Text | None:
        """Secondary info about this file (description, recipients, etc). Overload in subclasses."""
        return None

    @property
    def summary(self) -> Text:
        """Summary of this file for logging. Subclasses should extend with a method that closes the open '['."""
        txt = Text('').append(self._class_name, style=self._class_style)
        txt.append(f" {self.file_id}", style=FILENAME_STYLE)

        if self.timestamp:
            timestamp_str = remove_zero_time(self.timestamp).replace('T', ' ')
            txt.append(' (', style=SYMBOL_STYLE)
            txt.append(f"{timestamp_str}", style=TIMESTAMP_DIM).append(')', style=SYMBOL_STYLE)

        txt.append(' [').append(styled_key_value('size', Text(str(self.length), style='aquamarine1')))
        txt.append(", ").append(styled_key_value('lines', self.num_lines))

        if self.config and self.config.duplicate_of_id:
            txt.append(", ").append(styled_key_value('dupe_of', Text(self.config.duplicate_of_id, style='cyan dim')))

        return txt

    @property
    def summary_panel(self) -> Panel:
        """Panelized description() with info_txt(). Used in search results not in production HTML."""
        sentences = [self.summary]

        if self.INCLUDE_DESCRIPTION_IN_SUMMARY_PANEL:
            sentences += [Text('', style='italic').append(h) for h in self.info]

        return Panel(Group(*sentences), border_style=self._class_style, expand=False)

    @property
    def timestamp_sort_key(self) -> tuple[datetime, str, int]:
        """Sort by timestamp, file_id, then whether or not it's a duplicate file."""
        if self.duplicate_of_id:
            sort_id = self.duplicate_of_id
            dupe_idx = 1
        else:
            sort_id = self.file_id
            dupe_idx = 0

        return (self.timestamp or FALLBACK_TIMESTAMP, sort_id, dupe_idx)

    @property
    def _class_name(self) -> str:
        return type(self).__name__

    @property
    def _class_style(self) -> str:
        return DOC_TYPE_STYLES[self._class_name]

    @property
    def _debug_prefix(self) -> str:
        return underscore(self._class_name).lower()

    def __post_init__(self):
        if not self.file_path.exists():
            raise FileNotFoundError(f"File '{self.file_path}' does not exist!")

        self.file_info = FileInfo(self.file_path)
        self.text = self.text or self._load_file()
        self._set_text(text=self.text)
        self._repair()

        if self.config:
            for k, v in self.config.props_to_copy.items():
                setattr(self, k, v)

        self._extract_author()
        # TODO: Communication subclass sets FALLBACK_TIMESTAMP as default to keep type checking from whining :(
        self.timestamp = self._extract_timestamp() if self.timestamp in [None, FALLBACK_TIMESTAMP] else self.timestamp

    @classmethod
    def from_file_id(cls, file_id: str | int) -> Self:
        """Alternate constructor that finds the file path automatically and builds a `Document`."""
        return cls(coerce_file_path(file_id))

    def colored_external_links(self) -> Text:
        return self.file_info.build_external_links(include_alt_links=True)

    def file_info_panel(self) -> Group:
        """Panel with filename linking to raw file plus any additional info about the file."""
        links_txt = self.colored_external_links()
        panel = Panel(links_txt, border_style=self.border_style, expand=False)
        padded_info = [Padding(sentence, INFO_PADDING) for sentence in self.info]
        return Group(*([panel] + padded_info))

    def lines_matching(self, _pattern: re.Pattern | str) -> list[MatchedLine]:
        """Find lines in this file matching a regex pattern."""
        pattern = patternize(_pattern)
        return [MatchedLine(line, i) for i, line in enumerate(self.lines) if pattern.search(line)]

    def log(self, msg: str, level: int = logging.INFO) -> None:
        """Log a message with with this document's filename as a prefix."""
        logger.log(level, f"{self.file_id} {msg}")

    def log_top_lines(self, n: int = 10, msg: str = '', level: int = logging.INFO) -> None:
        """Log first 'n' lines of self.text at 'level'. 'msg' can be optionally provided."""
        separator = '\n\n' if '\n' in msg else '. '
        msg = (msg + separator) if msg else ''
        self.log(f"{msg}First {n} lines:\n\n{self.top_lines(n)}\n", level)

    def raw_text(self) -> str:
        """Reload the raw data from the underlying file and return it."""
        with open(self.file_path) as f:
            return f.read()

    def reload(self) -> Self:
        """Rebuild a new version of this object by loading the source file from disk again."""
        return type(self)(self.file_path)

    def repair_ocr_text(self, repairs: dict[str | re.Pattern, str], text: str) -> str:
        """Apply a dict of repairs (key is pattern or string, value is replacement string) to text."""
        for k, v in repairs.items():
            if isinstance(k, re.Pattern):
                text = k.sub(v, text)
            else:
                text = text.replace(k, v)

        return text

    def top_lines(self, n: int = 10) -> str:
        """First n lines."""
        return '\n'.join(self.lines[0:n])[:MAX_CHARS_TO_PRINT]

    def truncation_note(self, truncate_to: int) -> Text:
        """String with link to source URL that will replace the text after the truncation point."""
        link_markup = self.external_link_markup
        trim_note = f"<...trimmed to {truncate_to:,} characters of {self.length:,}, read the rest at {link_markup}...>"
        return Text.from_markup(wrap_in_markup_style(trim_note, 'dim'))

    def truthy_props(self, prop_names: list[str]) -> DebugDict:
        """Return key/value pairs but only if the value is truthy."""
        return {prop: getattr(self, prop) for prop in prop_names if getattr(self, prop)}

    def warn(self, msg: str) -> None:
        """Print a warning message prefixed by info about this `Document`."""
        self.log(msg, level=logging.WARNING)

    def _debug_dict(self) -> DebugDict:
        """Merge information about this document from config, file info, etc."""
        config_info = self.config.important_props if self.config else {}
        file_info = dict(self.file_info.as_dict)

        if config_info.get('id') == file_info.get('file_id'):
            config_info.pop('id')

        if file_info.get('source_url') == file_info.get('external_url', 'blah'):
            file_info.pop('external_url')

        config_info = prefix_keys(type(self.config).__name__, config_info)
        file_info = prefix_keys(underscore(FileInfo.__name__), file_info)
        return {**file_info, **config_info, **self._debug_props()}

    def _debug_props(self) -> DebugDict:
        """Collects props of this object only (not the config or locations)."""
        props = {k: getattr(self, k) for k in DEBUG_PROPS}
        props.update(self.truthy_props(DEBUG_PROPS_TRUTHY_ONLY))

        if self.file_info.file_size > 100 * 1024:
            props['file_size_str'] = self.file_info.file_size_str

        return prefix_keys(self._debug_prefix, props)

    def _debug_txt(self) -> Text:
        """Prettified version of `self._debug_dict()` suitable for printing."""
        txt_lines = styled_dict(self._debug_dict(), sep=': ')
        return prefix_with(txt_lines, ' ', pfx_style='grey', indent=2)

    def _extract_author(self) -> None:
        """Extended in `Email` subclass to pull from  headers."""
        pass

    def _extract_timestamp(self) -> datetime | None:
        """Should be implemented in subclasses."""
        pass

    def _load_file(self) -> str:
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        text = self.raw_text()
        text = text[1:] if (len(text) > 0 and text[0] == '\ufeff') else text  # remove BOM
        text = self.repair_ocr_text(OCR_REPAIRS, text.strip())

        lines = [
            line.strip() if self.STRIP_WHITESPACE else line for line in text.split('\n')
            if not (line.startswith(HOUSE_OVERSIGHT) or line.startswith('EFTA'))
        ]

        return collapse_newlines('\n'.join(lines))

    def _repair(self) -> None:
        """Can optionally be overloaded in subclasses to further improve self.text."""
        pass

    def _set_text(self, lines: list[str] | None = None, text: str | None = None) -> None:
        """Set `self.text` and `self.lines` based on arguments passed."""
        if lines and text:
            raise RuntimeError(f"[{self.filename}] Either 'lines' or 'text' arg must be provided (got both)")
        elif lines is not None:
            self.text = '\n'.join(lines).strip()
        elif text is not None:
            self.text = text.strip()
        else:
            raise RuntimeError(f"[{self.filename}] Either 'lines' or 'text' arg must be provided (neither was)")

        self.lines = [line.strip() if self.STRIP_WHITESPACE else line for line in self.text.split('\n')]

    def _write_clean_text(self, output_path: Path) -> None:
        """Write self.text to 'output_path'. Used only for diffing files."""
        if output_path.exists():
            if str(output_path.name).startswith(HOUSE_OVERSIGHT_PREFIX):
                raise RuntimeError(f"'{output_path}' already exists! Not overwriting.")
            else:
                logger.warning(f"Overwriting '{output_path}'...")

        with open(output_path, 'w') as f:
            f.write(self.text)

        logger.warning(f"Wrote {self.length} chars of cleaned {self.filename} to {output_path}.")

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Default `Document` renderer (Email and MessengerLog override this)."""
        yield self.file_info_panel()

        text_panel = Panel(
            self.prettified_text,
            border_style=self.border_style,
            expand=False,
            title=Text(f"({self.panel_title_timestamp})", style='dim') if self.panel_title_timestamp else None,
            title_align='right',
        )

        yield Padding(text_panel, (0, 0, 1, INFO_INDENT))

    def __str__(self) -> str:
        return self.summary.plain

    @classmethod
    def default_category(cls) -> str:
        return ''

    @classmethod
    def file_info_table(cls, title: str, first_col_name: str) -> Table:
        """Empty table with appropriate cols for summarizing groups of files."""
        table = build_table(title)
        cols = [{'name': first_col_name, 'min_width': 14}] + SUMMARY_TABLE_COLS
        add_cols_to_table(table, cols, 'right')
        return table

    @classmethod
    def files_info(cls, files: Sequence[Self], is_author_na: bool = False) -> dict[str, str | Text]:
        """Summary info about a group of files."""
        file_count = len(files)
        author_count = cls.known_author_count(files)

        return {
            'count': str(file_count),
            'author_count': NA_TXT if is_author_na else str(author_count),
            'no_author_count': NA_TXT if is_author_na else str(file_count - author_count),
            'uncertain_author_count': NA_TXT if is_author_na else str(len([f for f in files if f.is_attribution_uncertain])),
            'bytes': file_size_to_str(sum([f.file_info.file_size for f in files])),
        }

    @classmethod
    def files_info_row(cls, files: Sequence[Self], author_na: bool = False) -> Sequence[str | Text]:
        """Turn the values in the `cls.files_info()` dict into a list so they can be used as a table row."""
        return [v for v in cls.files_info(files, author_na).values()]

    @classmethod
    def known_author_count(cls, docs: Sequence[Self]) -> int:
        """Number of elements of `docs` that have an author attribution."""
        return len([doc for doc in docs if doc.author])

    @staticmethod
    def sort_by_id(docs: Sequence['DocumentType']) -> list['DocumentType']:
        return sorted(docs, key=lambda d: d.file_id)

    @staticmethod
    def sort_by_length(docs: Sequence['DocumentType']) -> list['DocumentType']:
        return sorted(docs, key=lambda d: d.file_info.file_size, reverse=True)

    @staticmethod
    def sort_by_timestamp(docs: Sequence['DocumentType']) -> list['DocumentType']:
        return sorted(docs, key=lambda doc: doc.timestamp_sort_key)

    @staticmethod
    def uniquify(documents: Sequence['DocumentType']) -> Sequence['DocumentType']:
        """Uniquify by file_id."""
        id_map = {doc.file_id: doc for doc in documents}
        return [doc for doc in id_map.values()]

    @staticmethod
    def without_dupes(docs: Sequence['DocumentType']) -> list['DocumentType']:
        """Remove any duplicate documents."""
        return [doc for doc in docs if not doc.is_duplicate]


DocumentType = TypeVar('DocumentType', bound=Document)
