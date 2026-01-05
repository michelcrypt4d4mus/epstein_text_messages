import re
import logging
import warnings
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Sequence

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
from epstein_files.util.doc_cfg import FINANCIAL_REPORTS_AUTHORS, DocCfg, Metadata
from epstein_files.util.data import escape_single_quotes, remove_timezone, sort_dict, uniquify
from epstein_files.util.file_helper import FILENAME_LENGTH
from epstein_files.util.env import args
from epstein_files.util.highlighted_group import styled_category
from epstein_files.util.rich import QUESTION_MARK_TXT, build_table, highlighter
from epstein_files.util.logging import logger

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

UNINTERESTING_CATEGORES = [
    ARTS,
    BOOK,
    JUNK,
    SKYPE_LOG,
    SPEECH,
]

# OtherFiles whose description/hints match these prefixes are not displayed unless --all-other-files is used
UNINTERESTING_PREFIXES = FINANCIAL_REPORTS_AUTHORS + [
    'article about',
    ARTICLE_DRAFT,
    'Aviation International',
    BBC,
    BLOOMBERG,
    'Boston Globe',
    BROCKMAN_INC,
    CHINA_DAILY,
    CNN,
    'completely redacted',
    CVRA,
    DAILY_MAIL,
    DAILY_TELEGRAPH,
    CVRA_LEXIS_SEARCH[0:-12],  # Because date at end :(
    DERSH_GIUFFRE_TWEET,
    'Financial Times',
    'Forbes',
    'Frontlines',
    'Future Science',
    'Globe and Mail',
    GORDON_GETTY,
    f"{HARVARD} Econ",
    HARVARD_POETRY,
    'Inference',
    JASTA,
    'JetGala',
    JOHN_BOLTON_PRESS_CLIPPING,
    'Journal of Criminal',
    LA_TIMES,
    'Litigation Daily',
    LAWRENCE_KRAUSS,
    LAWRENCE_KRAUSS_ASU_ORIGINS,
    'MarketWatch',
    MARTIN_NOWAK,
    'Morning News',
    NOBEL_CHARITABLE_TRUST,
    'Nautilus',
    'New Yorker',
    NYT,
    PALM_BEACH_CODE_ENFORCEMENT,
    PALM_BEACH_DAILY_NEWS,
    PALM_BEACH_POST,
    PALM_BEACH_TSV,
    PALM_BEACH_WATER_COMMITTEE,
    PAUL_KRASSNER,
    PEGGY_SIEGAL,
    'Politifact',
    'Rafanelli',
    ROBERT_LAWRENCE_KUHN,
    ROBERT_TRIVERS,
    'SCMP',
    'SciencExpress',
    'Scowcroft',
    SHIMON_POST_ARTICLE,
    SINGLE_PAGE,
    STACEY_PLASKETT,
    'Tatler',
    TERJE_ROD_LARSEN,
    TEXT_OF_US_LAW,
    TRANSLATION,
    TWEET,
    THE_REAL_DEAL_ARTICLE,
    TRUMP_DISCLOSURES,
    UBS_CIO_REPORT,
    UN_GENERAL_ASSEMBLY,
    'U.S. News',
    'US Office',
    'Vanity Fair',
    VI_DAILY_NEWS,
    WAPO,
]


@dataclass
class OtherFile(Document):
    """File that is not an email, an iMessage log, or JSON data."""

    def __post_init__(self):
        super().__post_init__()

        if self.config is None and VI_DAILY_NEWS_REGEX.search(self.text):
            self.log(f"Creating synthetic config for VI Daily News article...", logging.INFO)
            self.config = DocCfg(id=self.file_id, author=VI_DAILY_NEWS, category=ARTICLE, description='article')

    def category(self) -> str | None:
        return self.config and self.config.category

    def category_txt(self) -> Text | None:
        return styled_category(self.category() or UNKNOWN)

    def configured_description(self) -> str | None:
        """Overloads superclass method."""
        if self.config is not None:
            return self.config.info_str()

    def description_panel(self, include_hints=True) -> Panel:
        """Panelized description() with info_txt(), used in search results."""
        return super().description_panel(include_hints=include_hints)

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
        hints = self.hints()

        if self.is_duplicate:
            return False
        elif len(hints) == 0:
            return True
        elif self.config:
            if self.config.is_interesting:
                return True
            elif self.category() == FINANCE and self.author is not None:
                return False
            elif self.category() in UNINTERESTING_CATEGORES:
                return False

        for prefix in UNINTERESTING_PREFIXES:
            if hints[0].plain.startswith(prefix):
                return False

        return True

    def metadata(self) -> Metadata:
        metadata = super().metadata()
        metadata['is_interesting'] = self.is_interesting()
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

        timestamps: list[datetime] = []

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", module="datefinder")
            warnings.filterwarnings("ignore", module="dateutil")

            try:
                for timestamp in datefinder.find_dates(self.text, strict=True):
                    timestamp = remove_timezone(timestamp)

                    if MIN_TIMESTAMP < timestamp < MAX_TIMESTAMP:
                        timestamps.append(timestamp)

                    if len(timestamps) >= MAX_EXTRACTED_TIMESTAMPS:
                        break
            except ValueError as e:
                logger.warning(f"Error while iterating through datefinder.find_dates(): {e}")

        if len(timestamps) == 0:
            if not self.is_duplicate and VAST_HOUSE not in self.text:
                self.log_top_lines(15, msg=f"No timestamps found", level=logging.INFO)

            return None
        elif len(timestamps) == 1:
            return timestamps[0]
        else:
            timestamps = sorted(uniquify(timestamps), reverse=True)
            self._log_extracted_timestamps_info(timestamps)
            return timestamps[0]  # Most recent timestamp appearing in text is usually the closest

    def _log_extracted_timestamps_info(self, timestamps: list[datetime]) -> None:
        num_days_spanned = (timestamps[0] - timestamps[-1]).days
        timestamps_log_msg = f"Extracted {len(timestamps)} timestamps spanning {num_days_spanned} days{TIMESTAMP_LOG_INDENT}"
        timestamps_log_msg += TIMESTAMP_LOG_INDENT.join([str(dt) for dt in timestamps])

        if num_days_spanned > MAX_DAYS_SPANNED_TO_BE_VALID and VAST_HOUSE not in self.text:
            self.log_top_lines(15, msg=timestamps_log_msg, level=logging.DEBUG)

    @staticmethod
    def build_table(files: Sequence['OtherFile']) -> Table:
        """Build a table of OtherFile documents."""
        table = build_table(None, show_lines=True)
        table.add_column('File', justify='center', width=FILENAME_LENGTH)
        table.add_column('Date', justify='center')
        table.add_column('Size', justify='center')
        table.add_column('Type', justify='center')
        table.add_column(FIRST_FEW_LINES, justify='left', style='pale_turquoise4')

        for file in files:
            link_and_info = [file.raw_document_link_txt()]
            date_str = file.date_str()

            if file.is_duplicate:
                preview_text = file.duplicate_file_txt()
                row_style = ' dim'
            else:
                link_and_info += file.hints()
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

        for file in files:
            if file.category() is None:
                logger.warning(f"file {file.file_id} has no category")

            counts[file.category()] += 1

        table = build_table('File Counts by Category')
        table.add_column('Category', justify='right')
        table.add_column('Count', justify='center', width=25)

        for (category, count) in sort_dict(counts):
            table.add_row(styled_category(category or UNKNOWN), str(count))

        return table
