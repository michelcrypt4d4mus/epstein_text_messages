import logging
import warnings
from dataclasses import dataclass
from datetime import datetime

import datefinder
import dateutil
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, WHITESPACE_REGEX, Document
from epstein_files.util.constants import ARTS, BOOK, FINANCE, JUNK, SPEECH, UNINTERESTING_PREFIXES
from epstein_files.util.data import escape_single_quotes, remove_timezone, uniquify
from epstein_files.util.env import args, logger
from epstein_files.util.rich import highlighter, logger

MAX_EXTRACTED_TIMESTAMPS = 100
MAX_DAYS_SPANNED_TO_BE_VALID = 10
MIN_TIMESTAMP = datetime(2000, 1, 1)
MID_TIMESTAMP = datetime(2007, 1, 1)
MAX_TIMESTAMP = datetime(2022, 12, 31)
PREVIEW_CHARS = int(580 * (1 if args.all_other_files else 1.5))
LOG_INDENT = '\n         '
TIMESTAMP_LOG_INDENT = f'{LOG_INDENT}    '
VAST_HOUSE = 'vast house'  # Michael Wolff article draft about Epstein indicator

UNINTERESTING_CATEGORES = [
    ARTS,
    BOOK,
    JUNK,
    SPEECH,
]


@dataclass
class OtherFile(Document):
    """File that is not an email, an iMessage log, or JSON data."""

    def category(self) -> str | None:
        return self.config and self.config.category

    def configured_description(self) -> str | None:
        """Overloads superclass method."""
        if self.config is None:
            return None

        if self.category() == BOOK and self.config.author and self.config.description:
            title = self.config.description if '"' in self.config.description else f'"{self.config.description}"'
            return f"{BOOK}: {title} by {self.config.author}"

        pieces = [p for p in [self.config.author, self.config.description] if p]
        return ' '.join(pieces) if pieces else None

    def summary(self) -> Text:
        """One line summary mostly for logging."""
        return super().summary().append(CLOSE_PROPERTIES_CHAR)

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
        elif self.config:
            if self.config.is_interesting:
                return True
            elif self.config.category == FINANCE and self.config.author is not None:
                return False
            elif self.config.category in UNINTERESTING_CATEGORES:
                return False

        for prefix in UNINTERESTING_PREFIXES:
            if hints[0].plain.startswith(prefix):
                return False

        return True

    def preview_text(self) -> str:
        return WHITESPACE_REGEX.sub(' ', self.text)[0:PREVIEW_CHARS]

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
            self.log_top_lines(15, msg=f"{self.file_id}: No timestamps found", level=logging.INFO)
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
            log_level = logging.DEBUG if VAST_HOUSE in self.text else logging.INFO
            self.log_top_lines(15, msg=timestamps_log_msg, level=log_level)
