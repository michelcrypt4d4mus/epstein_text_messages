import logging
import re
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from subprocess import run
from typing import Callable, ClassVar, Self, Sequence, TypeVar

from rich.console import Console, ConsoleOptions, Group, RenderResult
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from epstein_files.documents.documents.doc_cfg import DUPE_TYPE_STRS, EmailCfg, DocCfg, Metadata, TextCfg
from epstein_files.documents.documents.doc_locations import DocLocation
from epstein_files.documents.documents.search_result import MatchedLine
from epstein_files.documents.emails.constants import FALLBACK_TIMESTAMP
from epstein_files.documents.emails.email_header import DETECT_EMAIL_REGEX
from epstein_files.output.rich import (INFO_STYLE, NA_TXT, SKIPPED_FILE_MSG_PADDING, SYMBOL_STYLE,
     add_cols_to_table, build_table, console, highlighter, join_texts, styled_key_value, link_text_obj,
     parenthesize, wrap_in_markup_style)
from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import CONFIGS_BY_ID, DOJ_FILE_STEM_REGEX, MAX_CHARS_TO_PRINT
from epstein_files.util.helpers.data_helpers import collapse_newlines, date_str, patternize, remove_zero_time, without_falsey
from epstein_files.util.env import DOCS_DIR, DOJ_PDFS_20260130_DIR
from epstein_files.util.helpers.file_helper import (coerce_file_path, extract_file_id, file_size, file_size_str,
     file_size_to_str, is_local_extract_file)
from epstein_files.util.logging import DOC_TYPE_STYLES, FILENAME_STYLE, logger

ALT_LINK_STYLE = 'white dim'
CHECK_LINK_FOR_DETAILS = 'not shown here, check original PDF for details'
CLOSE_PROPERTIES_CHAR = ']'
HOUSE_OVERSIGHT = HOUSE_OVERSIGHT_PREFIX.replace('_', ' ').strip()
DOJ_DATASET_ID_REGEX = re.compile(r"(?:epstein_dataset_|DataSet )(\d+)")
WHITESPACE_REGEX = re.compile(r"\s{2,}|\t|\n", re.MULTILINE)

EMPTY_LENGTH = 15
INFO_INDENT = 2
INFO_PADDING = (0, 0, 0, INFO_INDENT)
MIN_DOCUMENT_ID = 10477

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
    {'name': 'Uncertain Author', 'style': 'royal_blue1 dim'},
    {'name': 'Size', 'justify': 'right', 'style': 'dim'},
]


@dataclass
class Document:
    """
    Base class for all Epstein Files documents.

    Attributes:
        file_path (Path): Local path to file
        author (Name): Who is responsible for the text in the file
        config (DocCfg, optional): Preconfigured information about this file
        doj_2026_dataset_id (int, optional): Only set for files that came from the DOJ website.
        file_id (str): ID string - 6 numbers with zero padding for HOUSE_OVERSIGHT, full EFTAXXXXX for DOJ files.
        lines (list[str]): Number of lines in the file after all the cleanup
        text (str): Contents of the file
        timestamp (datetime, optional): When the file was originally created
        url_slug (str): Version of the filename that works in links to epsteinify etc.
    """
    file_path: Path
    file_id: str = field(init=False)
    lines: list[str] = field(default_factory=list)
    text: str = ''

    # Optional fields
    author: Name = None
    config: EmailCfg | DocCfg | TextCfg | None = None
    doj_2026_dataset_id: int | None = None
    timestamp: datetime | None = None
    url_slug: str = ''

    # Class variables
    include_description_in_summary_panel: ClassVar[bool] = False
    strip_whitespace: ClassVar[bool] = True  # Overridden in JsonFile

    @property
    def border_style(self) -> str:
        """Should be overloaded in subclasses."""
        return 'white'

    @property
    def config_description(self) -> str | None:
        if self.config and self.config.description:
            return f"({self.config.description})"

    @property
    def config_timestamp(self) -> datetime | None:
        """Configured timestamp, if any."""
        return self.config.timestamp if self.config and self.config.timestamp else None

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
    def external_link_txt(self) -> Text:
        return Text.from_markup(self.external_link_markup)

    @property
    def external_link_markup(self) -> str:
        """Rich markup string with link to source document."""
        return link_markup(self.external_url, coerce_file_stem(self.filename))

    @property
    def external_url(self) -> str:
        """The primary external URL to use when linking to this document's source."""
        if self.is_doj_file and self.doj_2026_dataset_id:
            return doj_2026_file_url(self.doj_2026_dataset_id, self.url_slug)
        else:
            return epstein_media_doc_url(self.url_slug)

    @property
    def filename(self) -> str:
        return self.file_path.name

    @property
    def file_id_debug_info(self) -> str:
        return ', '.join([f"{prop}={getattr(self, prop)}" for prop in ['file_id', 'filename', 'url_slug']])

    @property
    def file_size(self) -> int:
        return file_size(self.file_path)

    @property
    def file_size_str(self, decimal_places: int | None = None) -> str:
        return file_size_str(self.file_path, decimal_places)

    @property
    def info(self) -> list[Text]:
        """0 to 2 sentences containing the info_txt() as well as any configured description."""
        return without_falsey([
            self.info_txt,
            highlighter(Text(self.config_description, style=INFO_STYLE)) if self.config_description else None
        ])

    @property
    def info_txt(self) -> Text | None:
        """Secondary info about this file (description, recipients, etc). Overload in subclasses."""
        return None

    @property
    def is_attribution_uncertain(self) -> bool:
        return bool(self.config and self.config.is_attribution_uncertain)

    @property
    def is_doj_file(self) -> bool:
        return bool(DOJ_FILE_STEM_REGEX.match(self.file_id))

    @property
    def is_duplicate(self) -> bool:
        return bool(self.duplicate_of_id)

    @property
    def is_empty(self) -> bool:
        return len(self.text.strip()) < EMPTY_LENGTH

    @property
    def is_interesting(self) -> bool:
        return bool(self.config and self.config.is_interesting)

    @property
    def is_local_extract_file(self) -> bool:
        """True if extracted from other file (identifiable from filename e.g. HOUSE_OVERSIGHT_012345_1.txt)."""
        return is_local_extract_file(self.filename)

    @property
    def length(self) -> int:
        return len(self.text)

    @property
    def local_pdf_path(self) -> Path | None:
        """Path to the source PDF (only applies to DOJ files that were manually extracted)."""
        if not self.is_doj_file:
            return None

        return next((p for p in DOJ_PDFS_20260130_DIR.glob('**/*.pdf') if p.stem == self.file_path.stem), None)

    @property
    def locations(self) -> DocLocation:
        return DocLocation(
            local_path=self.file_path,
            local_pdf_path=self.local_pdf_path,
            external_url=self.external_url
        )

    @property
    def metadata(self) -> Metadata:
        metadata = self.config.metadata if self.config else {}
        metadata.update({k: v for k, v in asdict(self).items() if k in METADATA_FIELDS and v is not None})
        metadata['bytes'] = self.file_size
        metadata['filename'] = f"{self.url_slug}.txt"
        metadata['num_lines'] = self.num_lines
        metadata['type'] = self._class_name

        if self.is_local_extract_file:
            metadata['extracted_file'] = {
                'explanation': 'manually extracted from one of the other files',
                'extracted_from': self.url_slug + '.txt',
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
        style = INFO_STYLE if self.replace_text_with and len(self.replace_text_with) < 300 else ''
        text = self.replace_text_with or self.text
        trim_footer_txt = None

        if self.config and self.config.truncate_to:
            txt = highlighter(Text(text[0:self.config.truncate_to], style))
            trim_footer_txt = self.truncation_note(self.config.truncate_to)
            return txt.append('...\n\n').append(trim_footer_txt)
        else:
            return highlighter(Text(text, style))

    @property
    def replace_text_with(self) -> str | None:
        """Configured replacement text."""
        if self.config and self.config.replace_text_with:
            if self.config.author:
                text = f"{self.config.author} {self.config.replace_text_with}"
            else:
                text = self.config.replace_text_with

            if len(text) < 300:
                return f"(Text of {text} {CHECK_LINK_FOR_DETAILS})"
            else:
                return text

    @property
    def summary(self) -> Text:
        """Summary of this file for logging. Subclasses should extend with a method that closes the open '['."""
        txt = Text('').append(self._class_name, style=self._class_style)
        txt.append(f" {self.file_path.stem}", style=FILENAME_STYLE)

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
        """Panelized description() with info_txt(), used in search results."""
        sentences = [self.summary]

        if self.include_description_in_summary_panel:
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
        """Annoying workaround for circular import issues and isinstance()."""
        return str(type(self).__name__)

    @property
    def _class_style(self) -> str:
        return DOC_TYPE_STYLES[self._class_name]

    def __post_init__(self):
        if not self.file_path.exists():
            raise FileNotFoundError(f"File '{self.file_path.name}' does not exist!")

        self.file_id = extract_file_id(self.filename)
        # config and url_slug could have been pre-set in Email
        self.config = self.config or deepcopy(CONFIGS_BY_ID.get(self.file_id))
        self.url_slug = self.url_slug or self.filename.split('.')[0]

        # Extract the DOJ dataset ID from the path
        if self.is_doj_file:
            if (data_set_match := DOJ_DATASET_ID_REGEX.search(str(self.file_path))):
                self.doj_2026_dataset_id = int(data_set_match.group(1))
                logger.info(f"Extracted data set ID {self.doj_2026_dataset_id} for {self.url_slug}")
            else:
                self.warn(f"Couldn't find a data set ID in path '{self.file_path}'! Cannot create valid links.")

        self.text = self.text or self._load_file()
        self._set_computed_fields(text=self.text)
        self._repair()
        self._extract_author()
        self.timestamp = self.config_timestamp or self._extract_timestamp()

    @classmethod
    def from_file_id(cls, file_id: str | int) -> Self:
        """Alternate constructor that finds the file path automatically and builds a `Document`."""
        return cls(coerce_file_path(file_id))

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
        links = [link_text_obj(self.external_url, self.url_slug, style=style)]

        if include_alt_links:
            if self.doj_2026_dataset_id:
                jmail_url = jmail_doj_2026_file_url(self.doj_2026_dataset_id, self.file_id)
                jmail_link = link_text_obj(jmail_url, JMAIL, style=f"{style} dim" if style else ARCHIVE_LINK_COLOR)
                links.append(jmail_link)
            else:
                links.append(self.epsteinify_link(style=ALT_LINK_STYLE, link_txt=EPSTEINIFY))
                links.append(self.epstein_web_link(style=ALT_LINK_STYLE, link_txt=EPSTEIN_WEB))

                if self._class_name == 'Email':
                    links.append(self.rollcall_link(style=ALT_LINK_STYLE, link_txt=ROLLCALL))

        links = [links[0]] + [parenthesize(link) for link in links[1:]]
        base_txt = Text('', style='white' if include_alt_links else ARCHIVE_LINK_COLOR)
        return base_txt.append(join_texts(links))

    def file_info_panel(self) -> Group:
        """Panel with filename linking to raw file plus any additional info about the file."""
        panel = Panel(self.external_links_txt(include_alt_links=True), border_style=self.border_style, expand=False)
        padded_info = [Padding(sentence, INFO_PADDING) for sentence in self.info]
        return Group(*([panel] + padded_info))

    def log(self, msg: str, level: int = logging.INFO):
        """Log a message with with this document's filename as a prefix."""
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

    def printable_document(self) -> Self:
        """Overloaded by `DojFile` to convert some files to `Email` objects."""
        return self

    def raw_text(self) -> str:
        """Reload the raw data from the underlying file and return it."""
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

    def top_lines(self, n: int = 10) -> str:
        """First n lines."""
        return '\n'.join(self.lines[0:n])[:MAX_CHARS_TO_PRINT]

    def truncation_note(self, truncate_to: int) -> Text:
        """String with link that will replace the text after the truncation point."""
        link_markup = self.external_link_markup
        trim_note = f"<...trimmed to {truncate_to:,} characters of {self.length:,}, read the rest at {link_markup}...>"
        return Text.from_markup(wrap_in_markup_style(trim_note, 'dim'))

    def warn(self, msg: str) -> None:
        """Print a warning message prefixed by info about this `Document`."""
        self.log(msg, level=logging.WARNING)

    def _extract_author(self) -> None:
        """Get author from config. Extended in `Email` subclass to also check headers."""
        if self.config and self.config.author:
            self.author = self.config.author

    def _extract_timestamp(self) -> datetime | None:
        """Should be implemented in subclasses."""
        pass

    def _load_file(self) -> str:
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        text = self.raw_text()
        text = text[1:] if (len(text) > 0 and text[0] == '\ufeff') else text  # remove BOM
        text = self.repair_ocr_text(OCR_REPAIRS, text.strip())

        lines = [
            line.strip() if self.strip_whitespace else line for line in text.split('\n')
            if not (line.startswith(HOUSE_OVERSIGHT) or line.startswith('EFTA'))
        ]

        return collapse_newlines('\n'.join(lines))

    def _repair(self) -> None:
        """Can optionally be overloaded in subclasses to further improve self.text."""
        pass

    def _set_computed_fields(self, lines: list[str] | None = None, text: str | None = None) -> None:
        """Sets all fields derived from self.text based on either 'lines' or 'text' arg."""
        if lines and text:
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

        logger.warning(f"Wrote {self.length} chars of cleaned {self.filename} to {output_path}.")

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Default `Document` renderer (Email and MessengerLog override this)."""
        doc = self.printable_document()

        # Emails handle their own formatting
        if type(self) != type(doc):
            yield doc
        else:
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
            'uncertain_author_count': NA_TXT if is_author_na else str(len([f for f in files if f.is_attribution_uncertain])),
            'bytes': file_size_to_str(sum([f.file_size for f in files])),
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
    def is_email(doc: 'Document') -> bool:
        search_area = doc.text[0:5000]  # Limit search area to avoid pointless scans of huge files
        return isinstance(doc.config, EmailCfg) or bool(DETECT_EMAIL_REGEX.match(search_area) and doc.config is None)

    @staticmethod
    def known_author_count(docs: Sequence['Document']) -> int:
        """Count of how many Document objects have an author attribution."""
        return len([doc for doc in docs if doc.author])

    @staticmethod
    def sort_by_id(docs: Sequence['DocumentType']) -> list['DocumentType']:
        return sorted(docs, key=lambda d: d.file_id)

    @staticmethod
    def sort_by_length(docs: Sequence['DocumentType']) -> list['DocumentType']:
        return sorted(docs, key=lambda d: d.file_size, reverse=True)

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
        return [doc for doc in docs if not doc.is_duplicate]


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
