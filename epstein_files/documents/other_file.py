import re
import logging
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import ClassVar, Sequence

import datefinder
import dateutil
from rich.console import Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, Document
from epstein_files.documents.config.config_builder import build_cfg_from_text
from epstein_files.documents.config.doc_cfg import DocCfg, Metadata
from epstein_files.documents.documents.file_info import FileInfo
from epstein_files.output.epstein_highlighter import highlighter
from epstein_files.output.highlight_config import styled_category
from epstein_files.output.html.builder import table_to_html
from epstein_files.output.rich import build_table, console
from epstein_files.people.interesting_people import PERSONS_OF_INTEREST
from epstein_files.util.constant.strings import *
from epstein_files.util.constants import *
from epstein_files.util.helpers.data_helpers import days_between, coerce_utc_strict, uniquify, uniq_sorted
from epstein_files.util.helpers.debugging_helper import tz_debug_str
from epstein_files.util.helpers.file_helper import FILENAME_LENGTH
from epstein_files.util.helpers.rich_helpers import QUESTION_MARKS_TXT
from epstein_files.util.helpers.string_helper import DATE_LENGTH, collapse_whitespace, indented
from epstein_files.util.env import args, site_config
from epstein_files.util.logging import logger

FIRST_FEW_LINES = 'First Few Lines'
MAX_DAYS_SPANNED_TO_LOG_TOP_LINES = 10
MAX_EXTRACTED_TIMESTAMPS = 100
MIN_TIMESTAMP = coerce_utc_strict(datetime(2000, 1, 1))
MIN_PAGES_TO_TRUNCATE_PREVIEW = 10
TRUNCATED_PREVIEW_LEN = 200

# There's 3 spaces (2 for padding, one for divider) between each col and then 2 on each side + 1 indent
PREVIEW_COL_WIDTH = console.width - FILENAME_LENGTH - DATE_LENGTH - (3 * 2) - 6

SKIP_TIMESTAMP_EXTRACT = [
    PALM_BEACH_TSV,
    PALM_BEACH_PROPERTY_INFO,
]

# TODO: get rid of this
VAST_HOUSE = 'vast house'  # Michael Wolff article draft about Epstein indicator


@dataclass
class OtherFile(Document):
    """
    File that is not an email, an iMessage log, or JSON data.

    Attributes:
        derived_cfg (DocCfg, optional): a DocCfg object derived from contents of the file
    """
    derived_cfg: DocCfg | None = None

    # Class vars
    _INCLUDE_DESCRIPTION_IN_SUMMARY_PANEL: ClassVar[bool] = True                   # Overrides superclass
    MAX_TIMESTAMP: ClassVar[datetime] = coerce_utc_strict(datetime(2022, 12, 31))  # Overloaded in DojFile

    def __post_init__(self):
        super().__post_init__()

        if not self.config and (cfg := build_cfg_from_text(self)):
            self.derived_cfg = cfg

    @property
    def config(self) -> DocCfg | None:
        return super().config or self.derived_cfg

    @property
    def config_description(self) -> str:
        """Overloads superclass property."""
        if self.config and self.config.complete_description:
            pfx = 'Excerpt of ' if self.config.is_excerpt else ''
            return f"{pfx}{self.config.complete_description}"
        else:
            return ''

    @property
    def category_txt(self) -> Text:
        """Returns '???' for missing category."""
        # TODO: create synthetic DocCfg so we don't have to handle QUESTION_MARKS return here
        return styled_category(self.category) if self.category else QUESTION_MARKS_TXT

    @property
    def is_interesting(self) -> bool | None:
        """Junk emails are not interesting."""
        if (is_interesting := super().is_interesting) is not None:
            return is_interesting
        elif self.author is None and self.file_info.is_house_oversight_file:
            return True
        elif self.author is not None and self.author in PERSONS_OF_INTEREST:
            return True

    @property
    def is_valid_for_table(self) -> bool:
        """Return True if this file is OK to put in a table in the curated chronological views."""
        return not (self.config and (self.config.is_excerpt or self.config.show_full_panel))

    @property
    def metadata(self) -> Metadata:
        metadata = super().metadata
        metadata['is_interesting'] = self.is_interesting

        if self.extracted_timestamp:
            metadata['is_timestamp_inferred'] = True

        return metadata

    @property
    def preview_chars(self) -> str:
        """Text at start of file stripped of newlines for display in tables and other cramped settings."""
        num_chars = site_config.other_files_preview_chars
        text = self.text

        if self.config:
            if self.config.num_preview_chars:
                num_chars = self.config.num_preview_chars

            if self.config_display_text:
                text = self.config_display_text

        if text.count('Page') > MIN_PAGES_TO_TRUNCATE_PREVIEW:
            num_chars = TRUNCATED_PREVIEW_LEN

        return collapse_whitespace(text)[0:num_chars]

    @property
    def preview_txt(self) -> Text:
        txt = highlighter(escape(self.preview_chars))

        # TODO: should check self.length > len(self.preview_chars) but won't quite work with prettified text insertions
        if self.length > site_config.other_files_preview_chars and not self.config_display_text:
            txt.append(f"... ({self.length - len(txt):,} more characters)", 'dim italic')

        return txt

    @property
    def _summary(self) -> Text:
        """One line summary mostly for logging."""
        return super()._summary.append(CLOSE_PROPERTIES_CHAR)

    def extract_timestamp(self) -> datetime | None:
        """Return configured timestamp or value extracted by scanning text with datefinder."""
        timestamps: list[datetime] = []

        if self.config and any([s in self.config_description for s in SKIP_TIMESTAMP_EXTRACT]):
            return None

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", module="dateutil")

            try:
                # TODO: datefinder.find_dates() cannot find 08/29/2019 style e.g. in EFTA00005783 :(
                for dt in datefinder.find_dates(self.text, strict=False):
                    if MIN_TIMESTAMP < (dt := coerce_utc_strict(dt)) < self.MAX_TIMESTAMP:
                        timestamps.append(dt)

                    # Stop find_dates() once we've located a decent number of timestamps
                    if len(timestamps) >= MAX_EXTRACTED_TIMESTAMPS:
                        break
            except ValueError as e:
                self.warn(f"{e}\nError iterating over dateutil.find_dates(), using {len(timestamps)} timestamps found so far")

        return self._choose_extracted_timestamp(timestamps)

    def _choose_extracted_timestamp(self, timestamps: list[datetime]) -> datetime | None:
        """Most recent timestamp appearing in the text is usually the most likely to be correct."""
        timestamps = uniq_sorted(timestamps, reverse=True)

        if len(timestamps) == 0:
            if not (self.is_duplicate or VAST_HOUSE in self.text):
                self._log_top_lines(15, msg=f"No timestamps found")

            return None

        timestamp = timestamps[0]
        days_spanned = days_between(timestamps[-1], timestamp)

        if len(timestamps) == 1:
            log_msg = f"Found only one extracted timestamp '{timestamp}', returning it..."
        else:
            log_msg = f"Choosing '{timestamp}' from {len(timestamps)} extracted timestamps " \
                      f"spanning {days_spanned} days\n\n" + \
                      indented([tz_debug_str(dt) for dt in timestamps])

        if days_spanned > MAX_DAYS_SPANNED_TO_LOG_TOP_LINES:
            self._log_top_lines(10, msg=log_msg, level=logging.DEBUG)
        else:
            self.debug_log(log_msg)

        return timestamp

    @classmethod
    def files_preview_table(
        cls,
        files: Sequence['OtherFile'],
        title_pfx: str = '',
        title: str | Text | None = '',
        title_justify: str = '',
        **kwargs
    ) -> Table:
        """Build a table of `OtherFile` documents."""
        title = '' if title is None else (title or f'{title_pfx}Other Files Details in Chronological Order')
        title_justify = title_justify or ('left' if title else 'center')
        table = build_table(title, show_lines=True, title_justify=title_justify, **kwargs)
        table.add_column('File', justify='center', width=FILENAME_LENGTH)
        table.add_column('Info', justify='center', width=DATE_LENGTH)
        table.add_column(FIRST_FEW_LINES, justify='left', style='pale_turquoise4', width=PREVIEW_COL_WIDTH)

        for file in files:
            # call superclass method to avoid border_style rainbow
            link_and_info = [FileInfo.build_external_links(file.file_info, file.category_style, id_only=bool(args.mobile))]

            if file.date_str:
                date_txt = Text(file.date_str, style=TIMESTAMP_STYLE)
            else:
                date_txt = Text('(no date)', style=f"{TIMESTAMP_STYLE} dim italic")

            if file.is_duplicate:
                preview_text = file.duplicate_file_txt
                row_style = 'dim'
            else:
                preview_text = file.preview_txt
                row_style = ''
                link_and_info += file.info

            table.add_row(
                Group(*link_and_info),
                Group(date_txt, file.category_txt, Text(file.file_info.file_size_str, style='wheat4 dim')),
                preview_text,
                style=row_style
            )

        return cls._mobilize_table(table) if args.mobile else table

    @classmethod
    def files_preview_table_html(
        cls,
        files: Sequence['OtherFile'],
        title_pfx: str = '',
        title: str | Text | None = '',
        title_justify: str = '',
        **kwargs
    ) -> str:
        return table_to_html(cls.files_preview_table(files, title_pfx, title, title_justify, **kwargs))

    @classmethod
    def _mobilize_table(cls, _table: Table) -> Table:
        """Make a mobile version of the `files_preview_table()`."""
        table = build_table(_table.title, copy_props_from=_table)
        table.add_column('File', justify='center', width=len('EFTA00424931'))
        table.add_column(FIRST_FEW_LINES, justify='left', style='pale_turquoise4')
        max_col_idx = len(_table.columns) - 1

        for i, row in enumerate(_table.rows):
            table.add_row(
                # Collapse all but last col into one
                Group(
                    *[_table.columns[j]._cells[i] for j in range(1, max_col_idx)],
                    _table.columns[0]._cells[i],
                ),
                _table.columns[max_col_idx]._cells[i],
                style=row.style
            )

        return table

    @classmethod
    def summary_table(cls, files: Sequence['OtherFile'], title_pfx: str = '') -> Table:
        """Table showing file count by category."""
        categories = uniquify([f.category for f in files])
        categories = sorted(categories, key=lambda c: -len([f for f in files if f.category == c]))
        table = cls.files_summary_table(f'{title_pfx}Other Files Summary', 'Category')

        for category in categories:
            category_files = [f for f in files if f.category == category]
            table.add_row(styled_category(category), *cls.file_summary_row(category_files))

        table.columns = table.columns[:-2] + [table.columns[-1]]  # Removee unknown author col
        return table
