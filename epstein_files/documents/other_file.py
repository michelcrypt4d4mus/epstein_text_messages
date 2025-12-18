import logging
import re
from dataclasses import dataclass
from datetime import datetime

import datefinder
from rich.console import Console, ConsoleOptions, Group
from rich.markup import escape
from rich.text import Text

from epstein_files.documents.document import WHITESPACE_REGEX, Document
from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constants import DUPLICATE_FILE_IDS, FILE_DESCRIPTIONS, UNINTERESTING_PREFIXES
from epstein_files.util.data import escape_single_quotes, extract_datetime, ordinal_str, remove_timezone
from epstein_files.util.env import args, logger
from epstein_files.util.rich import console, highlighter, logger

PREVIEW_CHARS = int(520 * (1 if args.all_other_files else 1.5))
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)

MAX_EXTRACTED_TIMESTAMPS = 100
MAX_DAYS_SPANNED_TO_BE_VALID = 10
MIN_TIMESTAMP = datetime(1991, 1, 1)
MID_TIMESTAMP = datetime(2007, 1, 1)
MAX_TIMESTAMP = datetime(2022, 12, 31)


@dataclass
class OtherFile(Document):
    """Non email/iMessage log files."""

    def __post_init__(self):
        super().__post_init__()
        self.timestamp = self._extract_timestamp()

    def is_interesting(self):
        """False for lame prefixes and duplicates."""
        hints = self.hints()

        if len(hints) == 0:
            return True
        elif self.file_id in DUPLICATE_FILE_IDS:
            return False

        for prefix in UNINTERESTING_PREFIXES:
            if hints[0].plain.startswith(prefix):
                return False

        return True

    def highlighted_preview_text(self) -> Text:
        try:
            return highlighter(escape(self.preview_text()))
        except Exception as e:
            logger.error(f"Failed to apply markup in string '{escape_single_quotes(self.preview_text())}'\n"
                         f"Original string: '{escape_single_quotes(self.preview_text())}'\n"
                         f"File: '{self.filename}'\n")

            return Text(escape(self.preview_text()))

    def preview_text(self) -> str:
        return WHITESPACE_REGEX.sub(' ', self.text)[0:PREVIEW_CHARS]

    def _extract_timestamp(self) -> datetime | None:
        timestamps: list[datetime] = []

        # Check for configured values
        if self.file_id in FILE_DESCRIPTIONS:
            timestamp = extract_datetime(FILE_DESCRIPTIONS[self.file_id])

            if timestamp:
                if timestamp.date != 1:  # Avoid hacky '-01' appended date strings for now
                    return timestamp
                else:
                    timestamps.append(timestamp)

        # Avoid scanning large TSVs for dates
        if self.file_id in FILE_DESCRIPTIONS and FILE_DESCRIPTIONS[self.file_id].startswith('TSV'):
            return timestamps[0] if timestamps else None

        try:
            for i, timestamp in enumerate(datefinder.find_dates(self.text, strict=True)):
                logger.debug(f"{self.file_id}: Found {ordinal_str(i + 1)} timestamp '{timestamp}'...")
                timestamp = remove_timezone(timestamp)

                if MIN_TIMESTAMP < timestamp < MAX_TIMESTAMP:
                    timestamps.append(timestamp)

                if len(timestamps) == MAX_EXTRACTED_TIMESTAMPS:
                    break
        except ValueError as e:
            logger.error(f"Error while iterating with datefinder: {e}")

        if len(timestamps) == 0:
            if 'vast house' not in self.text:
                self.log_top_lines(15, msg=f"{self.file_id}: No timestamps found", level=logging.WARNING)

            return None
        elif len(timestamps) == 1:
            return timestamps[0]

        timestamps = sorted(timestamps, reverse=True)
        timestamp_strs = [str(dt) for dt in timestamps]
        num_days_spanned = (timestamps[0] - timestamps[-1]).days

        if num_days_spanned > MAX_DAYS_SPANNED_TO_BE_VALID and 'vast house' not in self.text:
            msg = f"{self.file_id}: Found {len(timestamps)} timestamps spanning {num_days_spanned} days\n     "
            msg += '\n     '.join(timestamp_strs)
            self.log_top_lines(15, msg=msg, level=logging.INFO)

        return timestamps[0]  # Most recent timestamp in text should be closest
