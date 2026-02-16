import re
import logging
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import ClassVar, Sequence

import datefinder
from rich.console import Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, WHITESPACE_REGEX, Document
from epstein_files.documents.documents.doc_cfg import DocCfg, Metadata
from epstein_files.output.highlight_config import QUESTION_MARKS_TXT, styled_category
from epstein_files.output.rich import build_table, highlighter
from epstein_files.util.constant.strings import *
from epstein_files.util.constants import *
from epstein_files.util.helpers.data_helpers import days_between, remove_timezone, uniquify
from epstein_files.util.helpers.file_helper import FILENAME_LENGTH
from epstein_files.util.helpers.string_helper import has_line_starting_with
from epstein_files.util.env import args
from epstein_files.util.logging import logger

FIRST_FEW_LINES = 'First Few Lines'
MAX_DAYS_SPANNED_TO_BE_VALID = 10
MAX_EXTRACTED_TIMESTAMPS = 100
MIN_TIMESTAMP = datetime(2000, 1, 1)
MID_TIMESTAMP = datetime(2007, 1, 1)
LOG_INDENT = '\n         '
PREVIEW_CHARS = int(580 * (1 if args.all_other_files else 1.5))
TIMESTAMP_LOG_INDENT = f'{LOG_INDENT}    '
VAST_HOUSE = 'vast house'  # Michael Wolff article draft about Epstein indicator

LEGAL_FILING_REGEX = re.compile(r"^Case (\d+:\d+-.*?) Doc")
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)

SKIP_TIMESTAMP_EXTRACT = [
    PALM_BEACH_TSV,
    PALM_BEACH_PROPERTY_INFO,
]


@dataclass
class OtherFile(Document):
    """
    File that is not an email, an iMessage log, or JSON data.

    Attributes:
        derived_cfg (DocCfg, optional): a DocCfg object derived from contents of the file
        was_timestamp_extracted (bool): True if the timestamp was programmatically extracted (and could be wrong)
    """
    derived_cfg: DocCfg | None = None
    was_timestamp_extracted: bool = False

    # Class vars
    include_description_in_summary_panel: ClassVar[bool] = True  # Class var for logging output
    max_timestamp: ClassVar[datetime] = datetime(2022, 12, 31) # Overloaded in DojFile
    num_synthetic_cfgs_created: ClassVar[int] = 0

    @property
    def config(self) -> DocCfg | None:
        return super().config or self.derived_cfg

    @property
    def config_description(self) -> str:
        """Overloads superclass property."""
        return self.config.complete_description if self.config else ''

    @property
    def category_txt(self) -> Text:
        """Returns '???' for missing category."""
        # TODO: create synthetic DocCfg so we don't have to handle QUESTION_MARKS return here
        return QUESTION_MARKS_TXT if not (self.config and self.config.category) else self.config.category_txt

    @property
    def metadata(self) -> Metadata:
        metadata = super().metadata
        metadata['is_interesting'] = self.is_interesting

        if self.was_timestamp_extracted:
            metadata['was_timestamp_extracted'] = self.was_timestamp_extracted

        return metadata

    @property
    def preview_text(self) -> str:
        """Text at start of file stripped of newlinesfor display in tables and other cramped settings."""
        text = self.config.replace_text_with if (self.config and self.config.replace_text_with) else self.text
        return WHITESPACE_REGEX.sub(' ', text)[0:PREVIEW_CHARS]

    @property
    def preview_text_highlighted(self) -> Text:
        return highlighter(escape(self.preview_text))

    @property
    def summary(self) -> Text:
        """One line summary mostly for logging."""
        return super().summary.append(CLOSE_PROPERTIES_CHAR)

    def __post_init__(self):
        super().__post_init__()

        if not self.config:
            self.derived_cfg = self._build_derived_cfg()

    def _build_derived_cfg(self) -> DocCfg | None:
        """Create a `DocCfg` object if there is none configured and the contents warrant it."""
        cfg = None

        if VI_DAILY_NEWS_REGEX.search(self.text):
            cfg = DocCfg(id=self.file_id, author=VI_DAILY_NEWS, category=ARTICLE)
        elif has_line_starting_with(self.text, [VALAR_GLOBAL_FUND, VALAR_VENTURES], 2):
            cfg = DocCfg(id=self.file_id, author=VALAR_VENTURES, category=CRYPTO, description=f"is a {PETER_THIEL} fintech fund")
        elif (case_match := LEGAL_FILING_REGEX.search(self.text)):
            cfg = DocCfg(id=self.file_id, category=LEGAL, description=f"legal filing in case {case_match.group(1)}")
        elif self.lines[0].lower() == 'valuation report':
            cfg = DocCfg(id=self.file_id, description="Epstein investment portfolio valuation report")

        if cfg:
            self.warn(f"Built synthetic cfg: {cfg}")
            type(self).num_synthetic_cfgs_created += 1

        return cfg

    def _extract_timestamp(self) -> datetime | None:
        """Return configured timestamp or value extracted by scanning text with datefinder."""
        timestamps: list[datetime] = []

        if self.config and any([s in (self.config_description or '') for s in SKIP_TIMESTAMP_EXTRACT]):
            return None

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", module="dateutil")

            try:
                # TODO: datefinder.find_dates() cannot find 08/29/2019 style e.g. in EFTA00005783 :(
                for timestamp in datefinder.find_dates(self.text, strict=False):
                    timestamp = remove_timezone(timestamp)

                    if MIN_TIMESTAMP < timestamp < self.max_timestamp:
                        timestamps.append(timestamp)

                    if len(timestamps) >= MAX_EXTRACTED_TIMESTAMPS:
                        break
            except ValueError as e:
                self.warn(f"Error while iterating through datefinder.find_dates(): {e}")

        if len(timestamps) == 0:
            if not (self.is_duplicate or VAST_HOUSE in self.text):
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

    @classmethod
    def files_preview_table(cls, files: Sequence['OtherFile'], title_pfx: str = '', title: str = '') -> Table:
        """Build a table of `OtherFile` documents."""
        title = title or f'{title_pfx}Other Files Details in Chronological Order'
        table = build_table(title, show_lines=True, title_justify='left' if title else 'center')
        table.add_column('File', justify='center', width=FILENAME_LENGTH)
        table.add_column('Date', justify='center')
        table.add_column('Size', justify='right', style='dim')
        table.add_column('Category', justify='center')
        table.add_column(FIRST_FEW_LINES, justify='left', style='pale_turquoise4')

        for file in files:
            link_and_info = [cls.external_links_txt(file)]  # call superclass method to avoid border_style rainbow
            date_str = file.date_str

            if file.is_duplicate:
                preview_text = file.duplicate_file_txt
                row_style = ' dim'
            else:
                link_and_info += file.info
                preview_text = file.preview_text_highlighted
                row_style = ''

            table.add_row(
                Group(*link_and_info),
                Text(date_str, style=TIMESTAMP_STYLE) if date_str else QUESTION_MARKS_TXT,
                file.file_size_str,
                file.category_txt,
                preview_text,
                style=row_style
            )

        return table

    @classmethod
    def summary_table(cls, files: Sequence['OtherFile'], title_pfx: str = '') -> Table:
        """Table showing file count by category."""
        categories = uniquify([f.category for f in files])
        categories = sorted(categories, key=lambda c: -len([f for f in files if f.category == c]))
        table = cls.file_info_table(f'{title_pfx}Other Files Summary', 'Category')

        for category in categories:
            category_files = [f for f in files if f.category == category]
            table.add_row(styled_category(category), *cls.files_info_row(category_files))

        table.columns = table.columns[:-2] + [table.columns[-1]]  # Removee unknown author col
        return table
