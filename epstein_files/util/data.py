"""
Helpers for dealing with various kinds of data.
"""
import itertools
import re
from datetime import datetime, timezone
from dateutil import tz
from typing import TypeVar

from epstein_files.util.constant import names
from epstein_files.util.constant.strings import QUESTION_MARKS
from epstein_files.util.env import args
from epstein_files.util.logging import logger

T = TypeVar('T')

ISO_DATE_REGEX = re.compile(r'\d{4}-\d{2}(-\d{2})?')
MULTINEWLINE_REGEX = re.compile(r"\n{2,}")
CONSTANT_VAR_REGEX = re.compile(r"^[A-Z_]+$")
ALL_NAMES = [v for k, v in vars(names).items() if isinstance(v, str) and CONSTANT_VAR_REGEX.match(k)]

PACIFIC_TZ = tz.gettz("America/Los_Angeles")
TIMEZONE_INFO = {"PDT": PACIFIC_TZ, "PST": PACIFIC_TZ}  # Suppresses annoying warnings from parse() calls

all_elements_same = lambda _list: len(_list) == 0 or all(x == _list[0] for x in _list)
collapse_newlines = lambda text: MULTINEWLINE_REGEX.sub('\n\n', text)
date_str = lambda dt: dt.isoformat()[0:10] if dt else None
escape_double_quotes = lambda text: text.replace('"', r'\"')
escape_single_quotes = lambda text: text.replace("'", r"\'")
iso_timestamp = lambda dt: dt.isoformat().replace('T', ' ')
days_between = lambda dt1, dt2: (dt2 - dt1).days + 1
days_between_str = lambda dt1, dt2: f"{days_between(dt1, dt2)} day" + ('s' if days_between(dt1, dt2) > 1 else '')
remove_zero_time = lambda dt: dt.isoformat().removesuffix('T00:00:00')
uniquify = lambda _list: list(set(_list))
without_falsey = lambda _list: [e for e in _list if e]


def dict_sets_to_lists(d: dict[str, set]) -> dict[str, list]:
    return {k: sorted(list(v)) for k, v in d.items()}


def flatten(_list: list[list[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(_list))


def json_safe(d: dict) -> dict:
    return {
        'None' if k is None else k: v.isoformat() if isinstance(v, datetime) else v
        for k,v in d.items()
    }


def listify(listlike) -> list:
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


def patternize(_pattern: str | re.Pattern) -> re.Pattern:
    return _pattern if isinstance(_pattern, re.Pattern) else re.compile(fr"({_pattern})", re.IGNORECASE)


def remove_timezone(timestamp: datetime) -> datetime:
    if timestamp.tzinfo:
        timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
        logger.debug(f"    -> Converted to UTC: {timestamp}")

    return timestamp


def sort_dict(d: dict[str | None, int] | dict[str, int]) -> list[tuple[str | None, int]]:
    sort_key = lambda e: (e[0] or '').lower() if args.sort_alphabetical else [-e[1], (e[0] or '').lower()]
    return sorted(d.items(), key=sort_key)
