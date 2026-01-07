import re
import logging
import warnings
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import ClassVar, Sequence

import datefinder
import dateutil
from rich.console import Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, WHITESPACE_REGEX, Document
from epstein_files.util.constant.strings import *
from epstein_files.util.constants import *
from epstein_files.util.doc_cfg import DocCfg, Metadata
from epstein_files.util.data import days_between, escape_single_quotes, remove_timezone, sort_dict, uniquify
from epstein_files.util.file_helper import FILENAME_LENGTH, file_size_to_str
from epstein_files.util.env import args
from epstein_files.util.highlighted_group import styled_category
from epstein_files.util.rich import QUESTION_MARK_TXT, build_table, highlighter
from epstein_files.util.logging import logger

FIRST_FEW_LINES = 'First Few Lines'
MAX_DAYS_SPANNED_TO_BE_VALID = 10
MAX_EXTRACTED_TIMESTAMPS = 100
MIN_TIMESTAMP = datetime(2000, 1, 1)
MID_TIMESTAMP = datetime(2007, 1, 1)
MAX_TIMESTAMP = datetime(2022, 12, 31)
PREVIEW_CHARS = int(580 * (1 if args.all_other_files else 1.5))
LOG_INDENT = '\n         '
TIMESTAMP_LOG_INDENT = f'{LOG_INDENT}    '
VAST_HOUSE = 'vast house'  # Michael Wolff article draft about Epstein indicator
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)

SKIP_TIMESTAMP_EXTRACT = [
    PALM_BEACH_TSV,
    PALM_BEACH_PROPERTY_INFO,
]

UNINTERESTING_CATEGORIES = [
    ACADEMIA,
    ARTICLE,
    ARTS,
    BOOK,
    CONFERENCE,
    JUNK,
    POLITICS,
    SKYPE_LOG,
]

# OtherFiles whose descriptions/info match these prefixes are not displayed unless --all-other-files is used
UNINTERESTING_PREFIXES = [
    'article about',
    BROCKMAN_INC,
    CVRA,
    DERSH_GIUFFRE_TWEET,
    GORDON_GETTY,
    f"{HARVARD} Econ",
    HARVARD_POETRY,
    JASTA,
    LEXIS_NEXIS,
    NOBEL_CHARITABLE_TRUST,
    PALM_BEACH_CODE_ENFORCEMENT,
    PALM_BEACH_TSV,
    PALM_BEACH_WATER_COMMITTEE,
    TWEET,
    UN_GENERAL_ASSEMBLY,
    'US Office',
]

INTERESTING_AUTHORS = [
    EDWARD_JAY_EPSTEIN,
    EHUD_BARAK,
    JOI_ITO,
    NOAM_CHOMSKY,
    MICHAEL_WOLFF,
    SVETLANA_POZHIDAEVA,
]


@dataclass
class OtherFile(Document):
    """
    File that is not an email, an iMessage log, or JSON data.

    Attributes:
        was_timestamp_extracted (bool): True if the timestamp was programmatically extracted (and could be wrong)
    """
    was_timestamp_extracted: bool = False
    include_description_in_summary_panel: ClassVar[bool] = True  # Class var for logging output

    def __post_init__(self):
        super().__post_init__()

        if self.config is None and VI_DAILY_NEWS_REGEX.search(self.text):
            self.log(f"Creating synthetic config for VI Daily News article...")
            self.config = DocCfg(id=self.file_id, author=VI_DAILY_NEWS, category=ARTICLE, description='article')

    def category(self) -> str | None:
        return self.config and self.config.category

    def category_txt(self) -> Text | None:
        return styled_category(self.category() or UNKNOWN)

    def config_description(self) -> str | None:
        """Overloads superclass method."""
        if self.config is not None:
            return self.config.complete_description()

    def highlighted_preview_text(self) -> Text:
        try:
            return highlighter(escape(self.preview_text()))
        except Exception as e:
            logger.error(f"Failed to apply markup in string '{escape_single_quotes(self.preview_text())}'\n"
                         f"Original string: '{escape_single_quotes(self.preview_text())}'\n"
                         f"File: '{self.filename}'\n")

            return Text(escape(self.preview_text()))

    def is_interesting(self):
        """False for lame prefixes, duplicates, and other boring files."""
        info_sentences = self.info()

        if self.is_duplicate():
            return False
        elif len(info_sentences) == 0:
            return True
        elif self.config:
            if self.config.is_interesting is not None:
                return self.config.is_interesting
            elif self.config.author in INTERESTING_AUTHORS:
                return True
            elif self.category() == FINANCE and self.author is not None:
                return False
            elif self.category() in UNINTERESTING_CATEGORIES:
                return False

        for prefix in UNINTERESTING_PREFIXES:
            if info_sentences[0].plain.startswith(prefix):
                return False

        return True

    def metadata(self) -> Metadata:
        metadata = super().metadata()
        metadata['is_interesting'] = self.is_interesting()

        if self.was_timestamp_extracted:
            metadata['was_timestamp_extracted'] = self.was_timestamp_extracted

        return metadata

    def preview_text(self) -> str:
        return WHITESPACE_REGEX.sub(' ', self.text)[0:PREVIEW_CHARS]

    def summary(self) -> Text:
        """One line summary mostly for logging."""
        return super().summary().append(CLOSE_PROPERTIES_CHAR)

    def _extract_timestamp(self) -> datetime | None:
        """Return configured timestamp or value extracted by scanning text with datefinder."""
        if self.config and self.config.timestamp:
            return self.config.timestamp
        elif self.config and any([s in (self.config_description() or '') for s in SKIP_TIMESTAMP_EXTRACT]):
            return None

        timestamps: list[datetime] = []

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", module="dateutil")

            try:
                for timestamp in datefinder.find_dates(self.text, strict=True):
                    timestamp = remove_timezone(timestamp)

                    if MIN_TIMESTAMP < timestamp < MAX_TIMESTAMP:
                        timestamps.append(timestamp)

                    if len(timestamps) >= MAX_EXTRACTED_TIMESTAMPS:
                        break
            except ValueError as e:
                self.log(f"Error while iterating through datefinder.find_dates(): {e}", logging.WARNING)

        if len(timestamps) == 0:
            if not (self.is_duplicate() or VAST_HOUSE in self.text):
                self.log_top_lines(15, msg=f"No timestamps found")

            return None

        self.was_timestamp_extracted = True

        if len(timestamps) == 1:
            return timestamps[0]
        else:
            timestamps = sorted(uniquify(timestamps), reverse=True)
            self._log_extracted_timestamps_info(timestamps)
            return timestamps[0]  # Most recent timestamp appearing in text is usually the closest

    def _log_extracted_timestamps_info(self, timestamps: list[datetime]) -> None:
        num_days_spanned = days_between(timestamps[-1], timestamps[0])
        timestamps_log_msg = f"Extracted {len(timestamps)} timestamps spanning {num_days_spanned} days{TIMESTAMP_LOG_INDENT}"
        timestamps_log_msg += TIMESTAMP_LOG_INDENT.join([str(dt) for dt in timestamps])

        if num_days_spanned > MAX_DAYS_SPANNED_TO_BE_VALID and VAST_HOUSE not in self.text:
            self.log_top_lines(15, msg=timestamps_log_msg, level=logging.DEBUG)

    @staticmethod
    def files_preview_table(files: Sequence['OtherFile']) -> Table:
        """Build a table of OtherFile documents."""
        table = build_table('Other Files Details', show_lines=True)
        table.add_column('File', justify='center', width=FILENAME_LENGTH)
        table.add_column('Date', justify='center')
        table.add_column('Size', justify='center')
        table.add_column('Type', justify='center')
        table.add_column(FIRST_FEW_LINES, justify='left', style='pale_turquoise4')

        for file in files:
            link_and_info = [file.external_links_txt()]
            date_str = file.date_str()

            if file.is_duplicate():
                preview_text = file.duplicate_file_txt()
                row_style = ' dim'
            else:
                link_and_info += file.info()
                preview_text = file.highlighted_preview_text()
                row_style = ''

            table.add_row(
                Group(*link_and_info),
                Text(date_str, style=TIMESTAMP_DIM) if date_str else QUESTION_MARK_TXT,
                file.file_size_str(),
                file.category_txt(),
                preview_text,
                style=row_style
            )

        return table

    @staticmethod
    def count_by_category_table(files: Sequence['OtherFile']) -> Table:
        counts = defaultdict(int)
        category_bytes = defaultdict(int)

        for file in files:
            if file.category() is None:
                logger.warning(f"file {file.file_id} has no category")

            counts[file.category()] += 1
            category_bytes[file.category()] += file.file_size()

        table = build_table('Other Files Summary', ['Category', 'Count', 'Has Author', 'No Author', 'Size'])
        table.columns[0].min_width = 14
        table.columns[-1].style = 'dim'

        for (category, count) in sort_dict(counts):
            category_files = [f for f in files if f.category() == category]
            known_author_count = Document.known_author_count(category_files)

            table.add_row(
                styled_category(category or UNKNOWN),
                str(count),
                str(known_author_count),
                str(count - known_author_count),
                file_size_to_str(category_bytes[category]),
            )

        return table
