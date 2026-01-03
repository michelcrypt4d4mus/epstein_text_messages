"""
Helpers for dealing with various kinds of data.
"""
import itertools
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from dateutil import tz
from typing import TypeVar

from dateutil.parser import parse
from rich.text import Text

from epstein_files.util.constant import names
from epstein_files.util.env import args, logger

T = TypeVar('T')

ISO_DATE_REGEX = re.compile(r'\d{4}-\d{2}(-\d{2})?')
MULTINEWLINE_REGEX = re.compile(r"\n{2,}")
CONSTANT_VAR_REGEX = re.compile(r"^[A-Z_]+$")
ALL_NAMES = [v for k, v in vars(names).items() if isinstance(v, str) and CONSTANT_VAR_REGEX.match(k)]

PACIFIC_TZ = tz.gettz("America/Los_Angeles")
TIMEZONE_INFO = {"PST": PACIFIC_TZ, "PDT": PACIFIC_TZ}  # Suppresses annoying warnings from parse() calls


def collapse_newlines(text: str) -> str:
    return MULTINEWLINE_REGEX.sub('\n\n', text)


def date_str(timestamp: datetime | None) -> str | None:
    return timestamp.isoformat()[0:10] if timestamp else None


def dict_sets_to_lists(d: dict[str, set]) -> dict[str, list]:
    return {k: sorted(list(v)) for k, v in d.items()}


def extract_datetime(s: str) -> datetime | None:
    match = ISO_DATE_REGEX.search(s)

    if not match:
        return None

    date_str = match.group(0)

    if len(date_str) == 4:
        date_str += '-01-01'
    elif len(date_str) == 7:
        date_str += '-01'

    return parse(date_str, tzinfos=TIMEZONE_INFO)


def extract_last_name(name: str) -> str:
    if ' ' not in name:
        return name

    names = name.split()

    if names[-1].startswith('Jr') and len(names[-1]) <= 3:
        return ' '.join(names[-2:])
    else:
        return names[-1]


def flatten(_list: list[list[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(_list))


def iso_timestamp(dt: datetime) -> str:
    return dt.isoformat().replace('T', ' ')


def listify(listlike: list | str | Text | None) -> list:
    """Create a list of 'listlike'. Returns empty list if 'listlike' is None or empty string."""
    if isinstance(listlike, list):
        return listlike
    elif listlike is None:
        return [None]
    elif listlike:
        return [listlike]
    else:
        return []


def ordinal_str(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')

    return str(n) + suffix


def patternize(_pattern: str | re.Pattern):
    return _pattern if isinstance(_pattern, re.Pattern) else re.compile(rf"({_pattern})", re.IGNORECASE)


def remove_timezone(timestamp: datetime) -> datetime:
    if timestamp.tzinfo:
        timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
        logger.debug(f"    -> Converted to UTC: {timestamp}")

    return timestamp


def sort_dict(d: dict[str | None, int] | dict[str, int]) -> list[tuple[str | None, int]]:
    sort_key = lambda e: (e[0] or '').lower() if args.sort_alphabetical else [-e[1], (e[0] or '').lower()]
    return sorted(d.items(), key=sort_key)


@dataclass
class Timer:
    started_at: float = field(default_factory=lambda: time.perf_counter())
    checkpoint_at: float = field(default_factory=lambda: time.perf_counter())
    decimals: int = 2

    def print_at_checkpoint(self, msg: str) -> None:
        logger.warning(f"{msg} in {self.seconds_since_checkpoint()}")
        self.checkpoint_at = time.perf_counter()

    def seconds_since_checkpoint(self) -> str:
        return f"{(time.perf_counter() - self.checkpoint_at):.{self.decimals}f} seconds"

    def seconds_since_start(self) -> str:
        return f"{(time.perf_counter() - self.started_at):.{self.decimals}f} seconds"


escape_double_quotes = lambda text: text.replace('"', r'\"')
escape_single_quotes = lambda text: text.replace("'", r"\'")
uniquify = lambda _list: list(set(_list))
without_nones = lambda _list: [e for e in _list if e]
