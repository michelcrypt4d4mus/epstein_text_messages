import logging
import re
from dataclasses import dataclass
from datetime import datetime

from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.other_file import OtherFile
from epstein_files.util.env import args, logger

MAX_EXTRACTED_TIMESTAMPS = 100
MAX_DAYS_SPANNED_TO_BE_VALID = 10
MIN_TIMESTAMP = datetime(1991, 1, 1)
MID_TIMESTAMP = datetime(2007, 1, 1)
MAX_TIMESTAMP = datetime(2022, 12, 31)
PREVIEW_CHARS = int(520 * (1 if args.all_other_files else 1.5))
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)


@dataclass
class JsonFile(OtherFile):
    """File containing JSON data."""

    def info_txt(self) -> Text | None:
        return Text(f"(JSON data, possibly iMessage or similar app metadata)", style='dim')

    def is_interesting(self):
        return False
