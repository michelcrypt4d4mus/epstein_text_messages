import logging
import re
import warnings
from dataclasses import dataclass
from datetime import datetime

import datefinder
import dateutil
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, WHITESPACE_REGEX, Document
from epstein_files.util.constants import UNINTERESTING_PREFIXES
from epstein_files.util.data import escape_single_quotes, extract_datetime, ordinal_str, remove_timezone, uniquify
from epstein_files.util.env import args, logger
from epstein_files.util.rich import highlighter, logger

MAX_EXTRACTED_TIMESTAMPS = 100
MAX_DAYS_SPANNED_TO_BE_VALID = 10
MIN_TIMESTAMP = datetime(1991, 1, 1)
MID_TIMESTAMP = datetime(2007, 1, 1)
MAX_TIMESTAMP = datetime(2022, 12, 31)
PREVIEW_CHARS = int(580 * (1 if args.all_other_files else 1.5))
LOG_INDENT = '\n         '
TIMESTAMP_LOG_INDENT = f'{LOG_INDENT}    '
VAST_HOUSE = 'vast house'  # Michael Wolff article draft about Epstein indicator
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)



@dataclass
class OtherFile(Document):
    """File that is not an email, an iMessage log, or JSON data."""

    def __post_init__(self):
        super().__post_init__()
        self.timestamp = self._extract_timestamp()

    def description(self) -> Text:
        """One line summary mostly for logging."""
        return super().description().append(CLOSE_PROPERTIES_CHAR)

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
        """False for lame prefixes and duplicates."""
        hints = self.hints()

        if self.is_duplicate:
            return False
        elif len(hints) == 0:
            return True

        for prefix in UNINTERESTING_PREFIXES:
            if hints[0].plain.startswith(prefix):
                return False

        return True

    def preview_text(self) -> str:
        return WHITESPACE_REGEX.sub(' ', self.text)[0:PREVIEW_CHARS]

    def _extract_timestamp(self) -> datetime | None:
        """Return ISO date at end of configured description entry or value extracted by datefinder.find_dates()."""
        log_level = logging.DEBUG if VAST_HOUSE in self.text else logging.INFO
        timestamps: list[datetime] = []
        configured_timestamp = None

        # Check for configured values
        if self.config and self.config.timestamp:
            timestamp = self.config.timestamp

            if timestamp:
                # Avoid returning hacky '-01' appended strings in case datefinder finds something more accurate
                if timestamp.date != 1:
                    # return timestamp  # TODO: reenable, this is just so we can log what's being found
                    configured_timestamp = timestamp
                    timestamps.append(timestamp)
                else:
                    timestamps.append(timestamp)

            # Avoid scanning large TSVs for dates
            if self.config and self.config.description and self.config.description.startswith('TSV'):
                return timestamps[0] if timestamps else None

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", module="datefinder")
                warnings.filterwarnings("ignore", module="dateutil")

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
            self.log_top_lines(15, msg=f"{self.file_id}: No timestamps found", level=log_level)
            return None
        elif len(timestamps) == 1:
            return timestamps[0]

        timestamps = sorted(uniquify(timestamps), reverse=True)
        timestamp_strs = [str(dt) for dt in timestamps]
        num_days_spanned = (timestamps[0] - timestamps[-1]).days
        timestamps_log_msg = f"Extracted {len(timestamps)} timestamps spanning {num_days_spanned} days{TIMESTAMP_LOG_INDENT}"
        timestamps_log_msg += TIMESTAMP_LOG_INDENT.join(timestamp_strs)

        if num_days_spanned > MAX_DAYS_SPANNED_TO_BE_VALID and VAST_HOUSE not in self.text:
            self.log_top_lines(15, msg=timestamps_log_msg, level=log_level)

        # Most recent timestamp in text should be closest to accurate bc articles eetc. should only have dates of things that already happened
        last_timestamp = timestamps[0]

        if configured_timestamp:
            if configured_timestamp.date() == last_timestamp.date():
                self.log(f"Configured and found timestamp have same date '{configured_timestamp.date()}'")
            else:
                days_diff = (configured_timestamp - last_timestamp).days
                msg = ''

                if self.hints():
                    msg = "\n".join([hint.plain for hint in self.hints()]) + LOG_INDENT

                msg = f"Configured '{configured_timestamp.date()}' and last found '{last_timestamp.date()}' differ by {days_diff} days"
                msg += f"{LOG_INDENT}{timestamps_log_msg}\n"
                self.log(msg)

            return configured_timestamp

        return last_timestamp
