import logging
import re
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from email import policy
from email.parser import BytesParser
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import ClassVar, Generator, Mapping, Self, Sequence, TypeVar

from rich.align import Align
from inflection import underscore
from rich.console import Console, ConsoleOptions, Group, JustifyMethod, RenderResult
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from epstein_files.documents.config.doc_cfg import DEFAULT_TRUNCATE_TO, DUPE_TYPE_STRS, DebugDict, EmailCfg, DocCfg, Metadata
from epstein_files.documents.documents.file_info import FileInfo
from epstein_files.documents.documents.search_result import MatchedLine
from epstein_files.documents.emails.constants import DOJ_EMAIL_OCR_REPAIRS, FALLBACK_TIMESTAMP
from epstein_files.documents.emails.email_header import DETECT_EMAIL_REGEX
from epstein_files.output.highlight_config import HIGHLIGHTED_CONTACTS, get_style_for_category, get_style_for_name
from epstein_files.output.html.builder import VERTICAL_MARGIN_EMS
from epstein_files.output.layout_elements.file_display import BasePanel, FileDisplay
from epstein_files.output.rich import (INFO_STYLE, NA_TXT, SYMBOL_STYLE, add_cols_to_table, build_table, console,
     styled_key_value, prefix_with, snip_msg_txt, styled_dict)
from epstein_files.output.site.sites import EXTRACTS_BASE_URL
from epstein_files.people.interesting_people import PERSONS_OF_INTEREST, UNINTERESTING_AUTHORS
from epstein_files.people.names import Name
from epstein_files.util.constant.strings import *
from epstein_files.util.constants import CONFIGS_BY_ID
from epstein_files.util.env import args, site_config
from epstein_files.util.external_link import link_text_obj
from epstein_files.util.helpers.data_helpers import (CharRange, coerce_utc, coerce_utc_strict, date_str, patternize, prefix_keys,
     uniquify, uniq_sorted, without_falsey)
from epstein_files.util.helpers.file_helper import coerce_file_path, file_size_str, file_size_to_str
from epstein_files.util.helpers.string_helper import collapse_newlines, doublespace_lines, join_truthy, quote, timestamp_without_zero_hour
from epstein_files.util.logging import DOC_TYPE_STYLES, FILENAME_STYLE, logger
from epstein_files.util.logging_entity import LoggingEntity

CHECK_LINK_FOR_DETAILS = 'not shown here, check original PDF for details'
CLOSE_PROPERTIES_CHAR = ']'
HOUSE_OVERSIGHT = HOUSE_OVERSIGHT_PREFIX.replace('_', ' ').strip()
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
    'people',
    'timestamp',
]

DEBUG_PROPS_TRUTHY_ONLY = [
    AUTHOR,
    'category',
    'is_empty',
    'people',
]

METADATA_FIELDS = [
    AUTHOR,
    'file_id',
    'filename',
    'num_lines',
    'timestamp',
]

T = TypeVar('T', bound=str | Text)


@dataclass
class Document(LoggingEntity):
    """
    Base class for all Epstein Files documents.

    Attributes:
        file_path (Path): Local path to file
        extracted_author (Name): who created the text in this file, extracted from the text (AKA "not configured")
        extracted_timestamp (datetime, optional): When the file was originally created, extracted from the text
        file_info (FileInfo): Manages things having to do with the underlying file (paths, URLs, etc.)
        lines (list[str]): Number of lines in the file after all the cleanup
        text (str): Contents of the file
    """
    file_path: Path

    # Derived at instantiation time
    extracted_author: Name = None
    extracted_timestamp: datetime | None = None
    file_info: FileInfo = field(init=False)
    lines: list[str] = field(default_factory=list)
    text: str = ''

    # Class constants, overloaded in some subclasses
    MAX_TIMESTAMP: ClassVar[datetime] = coerce_utc_strict(datetime(2026, 1, 29))  # Cutoff for extract_timestamp()
    STRIP_WHITESPACE: ClassVar[bool] = True                                       # Should strip whitespace (overridden in JsonFile)
    _INCLUDE_DESCRIPTION_IN_SUMMARY_PANEL: ClassVar[bool] = False                 # For logging only

    def __post_init__(self):
        self.file_info = FileInfo(self.file_path)

        if self.file_info.has_file and not self.file_path.exists():
            raise FileNotFoundError(f"File '{self.file_path}' does not exist!")

        self._set_text(text=self.text or self._load_file())
        self._repair()
        self.extracted_author = None if self.author else self.extract_author()
        self.extracted_timestamp = None if self.timestamp else coerce_utc(self.extract_timestamp())

    @classmethod
    def from_file_id(cls, file_id: str | int) -> Self:
        """Alternate constructor that finds the file path automatically and builds a `Document`."""
        return cls(coerce_file_path(file_id))

    @property
    def author(self) -> Name:
        return self._config.author or self.extracted_author

    @property
    def border_style(self) -> str:
        """Should be overloaded in subclasses."""
        return 'white'

    @property
    def category(self) -> str:
        return self._config.category or self.default_category()

    @property
    def category_style(self) -> str:
        return get_style_for_category(self.category) or ''

    @property
    def config(self) -> DocCfg | None:
        """Get the configured `DocCfg` object for this file id (if any)."""
        return CONFIGS_BY_ID.get(self.file_id)

    # TODO: swap this in for config() when it's safe to do so
    @property
    def _config(self) -> DocCfg:
        """Like `self.config` but falls back to return empty `DocCfg` object."""
        return self.config or self.dummy_cfg()

    @property
    def colored_external_links(self) -> Text:
        """Collection of links to official and unofficial for this file concatenated into one `Text` object."""
        return self.file_info.build_external_links(with_alt_links=True)

    @property
    def config_display_text(self) -> str | None:
        """Configured replacement text."""
        if self._config.display_text:
            text = join_truthy(self._config.author, self._config.display_text)

            if len(text) < 300 and not text.startswith('photo'):
                return f"(Text of {text} {CHECK_LINK_FOR_DETAILS})"
            else:
                return text

    @property
    def date_str(self) -> str | None:
        return date_str(self.timestamp)

    @property
    def char_range_to_display(self) -> CharRange | None:
        """Index of first and last characters to show when printing this document."""
        return self._config.char_range

    @property
    def display_text(self) -> str:
        """Config overrides what text should be displayed."""
        return collapse_newlines(self._config.display_text or self.text)

    @property
    def duplicate_file_txt(self) -> Text | None:
        """If the file is a dupe make a nice message to explain what file it's a duplicate of."""
        if self.is_duplicate:
            # TODO: this link is incorrect for DOJ files
            link = link_text_obj(FileInfo.url_for_id(self.file_info.url_slug), self.file_id, 'royal_blue1')
            return self._skipped_file_txt(Text(f"{DUPE_TYPE_STRS[self.config.dupe_type]} ").append(link))

    @property
    def empty_file_txt(self) -> Text | None:
        """Overridden in DojFile."""
        pass

    @property
    def external_link_markup(self) -> str:
        """Rich markup string with link to source document."""
        return self.file_info.external_link_markup(get_style_for_name(self.author) if self.author else '')

    @property
    def external_link_txt(self) -> Text:
        return Text.from_markup(self.external_link_markup)

    @property
    def file_id(self) -> str:
        return self.file_info.file_id

    @property
    def file_id_panel(self) -> BasePanel:
        """The header panel printed before the body and subheaders with links and file ID etc."""
        return BasePanel(border_style=self.border_style, text=self.colored_external_links)

    @property
    def filename(self) -> str:
        return self.file_info.filename

    @property
    def html_margin_bottom(self) -> str:
        """Overloaded in `Email` for case of emails with attachments."""
        return VERTICAL_MARGIN_EMS

    @property
    def info(self) -> list[Text]:
        """0 to 2 sentences containing the info_txt() as well as any configured description."""
        return without_falsey([self.subheader, self._config.description_txt])

    @property
    def is_duplicate(self) -> bool:
        return bool(self._config.duplicate_of_id)

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
        If `self.config.is_of_interest` returns a boolean (not `None`) return that, otherwise:

            1. this doc is attached to an `Email`:                             false     (the interestingness of the `Email` decides)
            2. `self.author` in `UNINTERESTING_AUTHORS`:                       false
            3. `HOUSE_OVERSIGHT_XXXXX` files with no author or `DocCfg`:      **TRUE**
            4. the configured `show_with_name` in PERSONS_OF_INTEREST:        **TRUE**

        `None` is returned if no decision is made so subclasses can append additional conditions.
        """
        if (is_of_interest := self._config.is_of_interest) is not None:
            return is_of_interest
        elif self._config.attached_to_email_id:
            return False
        elif self.author in UNINTERESTING_AUTHORS:
            return False
        elif self.file_info.is_house_oversight_file and not (self.author or self.config):
            return True
        elif self._config.show_with_name in PERSONS_OF_INTEREST:
            return True
        else:
            return None

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
    def panel_title_timestamp(self) -> str:
        """Time or date shown in the `title` of the enclosing `Panel` when printing this `Document`."""
        if self.timestamp is None or self.timestamp == FALLBACK_TIMESTAMP:
            return ''
        elif self._config.timestamp:
            prefix = 'approximate' if self._config.date_uncertain else ''
        else:
            prefix = 'inferred'

        if all(unit == 0 for unit in [self.timestamp.hour, self.timestamp.minute, self.timestamp.second]):
            date_or_time = 'date'
        else:
            date_or_time = 'timestamp'

        return join_truthy(prefix, f"{date_or_time}: {timestamp_without_zero_hour(self.timestamp)}")

    @property
    def people(self) -> list[str]:
        """Names of people who either sent/received this email or are mentioned in it."""
        people = [self.author] if self.author else []
        text_to_scan = self.display_text

        # `DocCfg.people` prop overrides everything.
        if self._config.people:
            return self._config.people
        elif not self._config.is_valid_for_name_scan:
            return people
        elif self._config.description:  # Make sure to scan the description too
            text_to_scan = f"{self._config.description}\n{text_to_scan}"

        # Use `Contact` regexes to scan for the presence of people's names in `self.text`
        people.extend([c.name for c in HIGHLIGHTED_CONTACTS if c.highlight_regex.search(text_to_scan)])
        return uniq_sorted([p for p in people if p not in self._config.non_participants])

    @property
    def prettified_txt(self) -> Text:
        """Returns the string we want to print as the body of the document."""
        display_text = doublespace_lines(self.display_text)
        # TODO: do something better to give replacement_text have different style
        style = INFO_STYLE if self.config_display_text and len(self.config_display_text) < 300 else ''

        # char range slice of Text late in the game here preserves Text highlighting at boundaries
        char_range = self.char_range_to_display or (0, len(display_text))
        selected_txt = self._config.text_highlighter(Text(display_text, style))[char_range[0]:char_range[1]]
        pretty_txt = self._intro_txt(char_range[0]).append(selected_txt)

        # For debugging/choosing truncation points only
        if args.char_nums:
            pretty_txt = self._inject_line_numbers(pretty_txt, args.char_nums)

        if (footer_txt := self.trimmed_chars_txt(char_range[1])):
            pretty_txt.append('...\n\n').append(footer_txt)

        return pretty_txt

    @property
    def suppressed_txt(self) -> Text | None:
        """`Text` object to print if this documents is suppressed for various reasons."""
        return self.uninteresting_txt or self.duplicate_file_txt or self.empty_file_txt

    @property
    def subheader(self) -> Text | None:
        """Secondary info about this file (description, recipients, etc). Overload in subclasses."""
        return None

    @property
    def timestamp(self) -> datetime | None:
        """Configuration timestamp takes precedence over extracted / derived timestamp."""
        return self._config.timestamp or self.extracted_timestamp

    @property
    def timestamp_sort_key(self) -> tuple[datetime, str, int]:
        """Sort by timestamp, file_id, then whether or not it's a duplicate file."""
        if self._config.duplicate_of_id:
            sort_id = self._config.duplicate_of_id
            dupe_idx = 1
        else:
            sort_id = self.file_id
            dupe_idx = 0

        return (self.timestamp or FALLBACK_TIMESTAMP, sort_id, dupe_idx)

    @property
    def uninteresting_txt(self) -> Text | None:
        """Text to print for uninteresting files."""
        if self._config.attached_to_email_id:
            return self._skipped_file_txt(f"attached to {self._config.attached_to_email_id}")
        elif args._suppress_uninteresting and self._config.is_interesting is False:
            return self._skipped_file_txt("uninteresting")
        else:
            return None

    @property
    def _class_style(self) -> str:
        return DOC_TYPE_STYLES[self._class_name]

    @property
    def _debug_prefix(self) -> str:
        return underscore(self._class_name).lower()

    @property
    def _identifier(self) -> str:
        """Required `LoggingEntity` abstract method."""
        return self.file_id

    @property
    def _log_prefix(self) -> str:
        """`Overload default LoggingEntity` method."""
        return f"{self.file_id} {self._class_name}"

    @property
    def _summary(self) -> Text:
        """Summary of this file for logging. Subclasses should extend with a method that closes the open '['."""
        txt = Text('').append(self._class_name, style=self._class_style)
        txt.append(f" {self.file_id}", style=FILENAME_STYLE)

        if self.timestamp:
            timestamp_str = timestamp_without_zero_hour(self.timestamp)
            txt.append(' (', style=SYMBOL_STYLE)
            txt.append(f"{timestamp_str}", style=TIMESTAMP_DIM).append(')', style=SYMBOL_STYLE)

        txt.append(' [').append(styled_key_value('size', Text(str(self.length), style='aquamarine1')))
        txt.append(", ").append(styled_key_value('lines', self.num_lines))

        if self._config.duplicate_of_id:
            txt.append(", ").append(styled_key_value('dupe_of', Text(self._config.duplicate_of_id, style='cyan dim')))

        return txt

    @property
    def _summary_panel(self) -> Panel:
        """Panelized description() with info_txt(). Used in search results not in production HTML."""
        sentences = [self._summary]

        if self._INCLUDE_DESCRIPTION_IN_SUMMARY_PANEL:
            sentences += [Text('', style='italic').append(h) for h in self.info]

        return Panel(Group(*sentences), border_style=self._class_style, expand=False)

    def excerpt_text(self, char_range: CharRange | None = None, text: str = '', style = '') -> Text:
        """Create an excerpt of `text`, add appropriate header/footer if truncated, and highlight it."""
        char_range = char_range or (0, len(text))
        text = doublespace_lines(text or self.text)        # TODO: not ideal place for doublespace call
        excerpt_txt = self._intro_txt(char_range[0])
        excerpt_txt.append(Text(text, style)[char_range[0]:char_range[1]])  # array slice of `Text` obj preserves style

        if args.char_nums:    # For debugging/choosing truncation points
            excerpt_txt = self._inject_line_numbers(excerpt_txt, args.char_nums)

        if (footer_txt := self.trimmed_chars_txt(char_range[1])):
            excerpt_txt.append('...\n\n').append(footer_txt)

        return self._config.text_highlighter(excerpt_txt)

    def extract_author(self) -> Name:
        """Extended in `Email` subclass to pull from headers etc."""
        return None

    def extract_timestamp(self) -> datetime | None:
        """Should be implemented in subclasses."""
        return None

    def file_display(self, align: JustifyMethod | None = None) -> FileDisplay:
        """Allows for proper right vs. left justify."""
        body = BasePanel(
            border_style=self.border_style,
            text=self.prettified_txt,
            title=Text(f"({self.panel_title_timestamp})", style='dim') if self.panel_title_timestamp else None,
        )

        return FileDisplay(
            background_color=self.config.background_color if self.config else '',
            body_panel=body,
            file_info=self.file_id_panel,
            indent=site_config.info_indent,
            justify=align,
            margin_bottom=self.html_margin_bottom,
            subheaders=self.info,
        )

    def lines_matching(self, _pattern: re.Pattern | str) -> list[MatchedLine]:
        """Find lines in this file matching a regex pattern."""
        pattern = patternize(_pattern)
        return [MatchedLine(line, i) for i, line in enumerate(self.lines) if pattern.search(line)]

    def print(self, whole_file: bool = False) -> None:
        """Print this object for some suppression message."""
        if self._config.attached_to_email_id:
            self._warn(f"is an attachment and self.print() was calleed")
            return
        elif (suppressed_txt := self.suppressed_txt):
            console.print(Padding(suppressed_txt, site_config.suppressed_file_padding()))
            return

        # TODO: this approach to forcing whole_file sucks
        old_whole_file_arg = args.whole_file
        args.whole_file = args.whole_file or whole_file
        console.print(self)
        args.whole_file = old_whole_file_arg

    def raw_text(self) -> str:
        """Reload the raw data from the underlying file and return it."""
        if self.file_info.is_eml_file:
            with open(self.file_path, 'rb') as fp:
                return BytesParser(policy=policy.default).parse(fp).as_string()
        else:
            return self.file_path.read_text()

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

    def rich_header(self) -> Group:
        """Panel + subheaders with filename linking to raw file plus any additional info about the file."""
        padded_info = [Padding(sentence, site_config.info_padding()) for sentence in self.info]
        return Group(*([self.file_id_panel] + padded_info))

    def top_lines(self, n: int = 10) -> str:
        """First n lines."""
        return '\n'.join(self.lines[0:n])[:DEFAULT_TRUNCATE_TO]

    def to_html(self) -> str:
        # TODO: this does not include the timestamp for OtherFiles!
        return self.file_display().to_html()

    def trimmed_chars_txt(self, truncate_to: int) -> Text | None:
        """String with link to source URL that will replace the text after the truncation point."""
        if truncate_to >= len(self.text):
            return None
        else:
            msg = f"trimmed to {truncate_to:,} characters of {self.length:,}, read the rest at {self.external_link_markup}"
            return snip_msg_txt(msg)

    def truthy_props(self, prop_names: list[str]) -> DebugDict:
        """Return key/value pairs but only if the value is truthy."""
        return {prop: getattr(self, prop) for prop in prop_names if getattr(self, prop)}

    def _debug_dict(self, as_txt: bool = False, with_prefixes: bool = True) -> DebugDict | Text:
        """Merge information about this document from `DocCfg`, `FileInfo`, etc. objs."""
        config_info = self.config.truthy_props if self.config else {}
        file_info = self.file_info.as_dict

        # Remove duplicate fields to save space
        if config_info.get('id') == file_info.get('file_id'):
            del config_info['id']

        if file_info.get('source_url') == file_info.get('external_url', 'blah'):
            del file_info['external_url']

        if with_prefixes:
            config_info = prefix_keys(type(self.config).__name__, config_info)
            file_info = prefix_keys(underscore(FileInfo.__name__), file_info)

        props = {**config_info, **file_info, **self._debug_props()}
        return styled_dict(props) if as_txt else props

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

    def _inject_line_numbers(self, text: T, interval: int) -> T:
        """Inject character numbers markers into `text`. For debugging only."""
        idx = interval
        new_text = text[:idx]

        def line_marker(i: int) -> T:
            marker_str = f'\n\n ------ {idx} ------ \n\n'
            return Text(marker_str) if isinstance(text, Text) else marker_str

        while idx < len(text):
            new_text += line_marker(idx)
            end_idx = idx + interval
            new_text += text[idx:end_idx]
            idx = end_idx

        return new_text

    def _load_file(self) -> str:
        """Remove BOM and HOUSE OVERSIGHT lines, strip whitespace."""
        return self.raw_text()

    def _log_top_lines(self, n: int = 10, msg: str = '', level: int = logging.DEBUG) -> None:
        """Log first 'n' lines of self.text at 'level'. 'msg' can be optionally provided."""
        separator = '\n\n' if '\n' in msg else '. '
        msg = (msg + separator) if msg else ''
        self._log(f"{msg}First {n} lines of {self.file_id}:\n\n{self.top_lines(n)}\n", level)

    def _numbered_lines(self) -> str:
        """For logging."""
        return '\n'.join([f"[{i}] {quote(line)}" for i, line in enumerate(self.lines)])

    def _repair(self) -> None:
        """Can optionally be overloaded in subclasses to further improve self.text."""
        text = self.repair_ocr_text(OCR_REPAIRS, self.text.lstrip('\ufeff').strip())  # remove BOM

        lines = [
            line.strip() if self.STRIP_WHITESPACE else line for line in text.split('\n')
            if not (line.startswith(HOUSE_OVERSIGHT) or line.startswith(EFTA_PREFIX))
        ]

        self._set_text(text=collapse_newlines('\n'.join(lines)))

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

        # logger.debug(f"_set_text() set self.text to\n---\n{self.text}\n---")
        self.lines = [line.strip() if self.STRIP_WHITESPACE else line for line in self.text.split('\n')]

    def _skipped_file_txt(self, reason: str | Text) -> Text:
        txt = Text(f"Skipping ", f"{INFO_STYLE} dim").append(self.external_link_txt)
        return txt.append(" because it's ").append(reason)

    def _intro_txt(self, cutoff: int) -> Text:
        """Truncation message if it's an excerpt."""
        if cutoff == 0:
            return Text('')  # Empty Text object makes sure the whole string starts with default no-style

        return snip_msg_txt(f'trimmed first {cutoff:,} characters', EXCERPT_STYLE).append('\n\n...')

    def _write_clean_text(self, output_path: Path) -> None:
        """Write self.text to 'output_path'. Used only for diffing files."""
        if output_path.exists():
            if str(output_path.name).startswith(HOUSE_OVERSIGHT_PREFIX):
                raise RuntimeError(f"'{output_path}' already exists! Not overwriting.")
            else:
                logger.warning(f"Overwriting '{output_path}'...")

        with open(output_path, 'w') as f:
            f.write(self.text)
            self._log(f"Wrote {self.length} chars of self.text to '{output_path}'.")

    @contextmanager
    def _write_tmp_file(self) -> Generator[Path, None, None]:
        with NamedTemporaryFile(dir=self.file_path.parent) as tmp_doc_file:
            tmp_path = Path(tmp_doc_file.name)
            self._write_clean_text(tmp_path)
            self._log(f"created tmp file '{tmp_doc_file.name}' ({file_size_str(tmp_path)})")
            yield Path(tmp_doc_file.name)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        """Default `Document` renderer (Email and MessengerLog override this)."""
        yield self.file_display()

    def __str__(self) -> str:
        return self._summary.plain

    @classmethod
    def default_category(cls) -> str:
        return ''

    @classmethod
    def dummy_cfg(cls) -> DocCfg:
        """Empty config so you can call config methods without "if self.config and self.config.thing"."""
        return DocCfg(id='DUMMY')

    @classmethod
    def files_summary_table(cls, title: str | Text, first_col_name: str) -> Table:
        """Empty table with appropriate cols for summarizing groups of files."""
        table = build_table(title)
        cols = [{'name': first_col_name, 'min_width': 14}] + SUMMARY_TABLE_COLS
        add_cols_to_table(table, cols, 'right')
        # logger.warning(f'\n\ntable.title_justify={table.title_justify}, type(title)={type(title).__name__}, title={table.title}')

        # if isinstance(title, Text) and title.justify:
        #     logger.warning(f'        title is Text obj, justify={title.justify}\n\n')

        return table

    @classmethod
    def files_summary(cls, files: Sequence[Self], is_author_na: bool = False) -> dict[str, str | Text]:
        """Summary info about a group of files."""
        file_count = len(files)
        author_count = cls.known_author_count(files)

        # NOTE: Order matters!
        return {
            'count': str(file_count),
            'author_count': NA_TXT if is_author_na else str(author_count),
            'no_author_count': NA_TXT if is_author_na else str(file_count - author_count),
            'uncertain_author_count': NA_TXT if is_author_na else str(len([f for f in files if f._config.author_uncertain])),
            'bytes': file_size_to_str(sum([f.file_info.file_size for f in files])),
        }

    @classmethod
    def file_summary_row(cls, files: Sequence[Self], author_na: bool = False) -> Sequence[str | Text]:
        """Turn the values in the `cls.files_info()` dict into a list so they can be used as a table row."""
        return [v for v in cls.files_summary(files, author_na).values()]

    @classmethod
    def filter_for_type(cls, docs: Sequence['Document']) -> list[Self]:
        """Filter for Document objects of this class."""
        return [d for d in docs if isinstance(d, cls)]

    @classmethod
    def known_author_count(cls, docs: Sequence[Self]) -> int:
        """Number of elements of `docs` that have an author attribution."""
        return len([doc for doc in docs if doc.author])

    @staticmethod
    def count_by_month(docs: Sequence['DocumentType']) -> Counter[str | None]:
        return Counter([d.timestamp.date().isoformat()[0:7] if d.timestamp else None for d in docs])

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
