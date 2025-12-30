import logging
import re
from dataclasses import dataclass
from datetime import datetime

import datefinder
from rich.markup import escape
from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, WHITESPACE_REGEX, Document
from epstein_files.util.constants import DUPLICATE_FILE_IDS, FILE_DESCRIPTIONS, UNINTERESTING_PREFIXES
from epstein_files.util.data import escape_single_quotes, extract_datetime, ordinal_str, remove_timezone
from epstein_files.util.env import args, logger
from epstein_files.util.rich import highlighter, logger

MAX_EXTRACTED_TIMESTAMPS = 100
MAX_DAYS_SPANNED_TO_BE_VALID = 10
MIN_TIMESTAMP = datetime(1991, 1, 1)
MID_TIMESTAMP = datetime(2007, 1, 1)
MAX_TIMESTAMP = datetime(2022, 12, 31)
PREVIEW_CHARS = int(520 * (1 if args.all_other_files else 1.5))
VAST_HOUSE = 'vast house'  # Michael Wolff article draft about Epstein indicator
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)


@dataclass
class OtherFile(Document):
    """File that is neither an email nor an iMessage log."""

    def __post_init__(self):
        super().__post_init__()
        self.timestamp = self._extract_timestamp()

    def description(self) -> Text:
        """One line summary mostly for logging."""
        return super().description().append(CLOSE_PROPERTIES_CHAR)

    def highlighted_preview_text(self) -> Text:
        try:
            return highlighter(escape(self.preview_text()))
        except Exception as e:
            logger.error(f"Failed to apply markup in string '{escape_single_quotes(self.preview_text())}'\n"
                         f"Original string: '{escape_single_quotes(self.preview_text())}'\n"
                         f"File: '{self.filename}'\n")

            return Text(escape(self.preview_text()))

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

    def preview_text(self) -> str:
        return WHITESPACE_REGEX.sub(' ', self.text)[0:PREVIEW_CHARS]

    def _extract_timestamp(self) -> datetime | None:
        """Return ISO date at end of FILE_DESCRIPTIONS entry or value extracted by datefinder.find_dates()."""
        timestamps: list[datetime] = []

        # Check for configured values
        if self.file_id in FILE_DESCRIPTIONS:
            timestamp = extract_datetime(FILE_DESCRIPTIONS[self.file_id])

            if timestamp:
                # Avoid returning hacky '-01' appended strings in case datefinder finds something more accurate
                if timestamp.date != 1:
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
            logger.warning(f"Error while iterating through datefinder.find_dates(): {e}")

        if len(timestamps) == 0:
            if VAST_HOUSE not in self.text:
                self.log_top_lines(15, msg=f"{self.file_id}: No timestamps found", level=logging.WARNING)

            return None
        elif len(timestamps) == 1:
            return timestamps[0]

        timestamps = sorted(timestamps, reverse=True)
        timestamp_strs = [str(dt) for dt in timestamps]
        num_days_spanned = (timestamps[0] - timestamps[-1]).days

        if num_days_spanned > MAX_DAYS_SPANNED_TO_BE_VALID and VAST_HOUSE not in self.text:
            msg = f"{self.file_id}: Found {len(timestamps)} timestamps spanning {num_days_spanned} days\n     "
            msg += '\n     '.join(timestamp_strs)
            self.log_top_lines(15, msg=msg, level=logging.INFO)

        return timestamps[0]  # Most recent timestamp in text should be closest
