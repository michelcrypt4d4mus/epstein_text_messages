"""
Helpers for dealing with various kinds of data.
"""
import itertools
import re
from datetime import datetime, timezone
from dateutil import tz
from typing import Sequence, TypeVar

from epstein_files.util.constant import names
from epstein_files.util.env import args
from epstein_files.util.logging import logger

T = TypeVar('T')

ISO_DATE_REGEX = re.compile(r'\d{4}-\d{2}(-\d{2})?')
CONSTANT_VAR_REGEX = re.compile(r"^[A-Z_]+$")
ALL_NAMES = [v for k, v in vars(names).items() if isinstance(v, str) and CONSTANT_VAR_REGEX.match(k)]

AMERICAN_DATE_FORMAT = r"%m/%d/%y %I:%M:%S %p"
AMERICAN_TIME_REGEX = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4}\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)")
PACIFIC_TZ = tz.gettz("America/Los_Angeles")
TIMEZONE_INFO = {"PDT": PACIFIC_TZ, "PST": PACIFIC_TZ}  # Suppresses annoying warnings from parse() calls

all_elements_same = lambda _list: len(_list) == 0 or all(x == _list[0] for x in _list)
date_str = lambda dt: dt.isoformat()[0:10] if dt else None
escape_double_quotes = lambda text: text.replace('"', r'\"')
escape_single_quotes = lambda text: text.replace("'", r"\'")
days_between = lambda dt1, dt2: (dt2 - dt1).days + 1
days_between_str = lambda dt1, dt2: f"{days_between(dt1, dt2)} day" + ('s' if days_between(dt1, dt2) > 1 else '')
remove_zero_time = lambda dt: dt.isoformat().removesuffix('T00:00:00')
uniquify = lambda _list: list(set(_list))
without_falsey = lambda _list: [e for e in _list if e]


def constantize_names(s: str) -> str:
    """Replace occurences of 'Jeffrey Epstein' with '{JEFFREY_EPSTEIN}' etc."""
    for name in ALL_NAMES:
        s = s.replace(name, f"{{{names.constantize_name(name)}}}")

    return s


def dict_sets_to_lists(d: dict[str, set]) -> dict[str, list]:
    """Turn the `set` values in the dict into sorted lists."""
    return {k: sorted(list(v)) for k, v in d.items()}


def flatten(_list: Sequence[list[T] | set[T]]) -> list[T]:
    if not _list:
        return []
    elif all(isinstance(element, set) for element in _list):
        return list(set().union(*_list))
    else:
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


def prefix_keys(prefix: str, _dict: dict[str, T], sep='.') -> dict[str, T]:
    """Add `prefix` to the front of all the keys in `_dict`."""
    return {f"{prefix}{sep}{k}": v for k, v in _dict.items()}


def remove_timezone(timestamp: datetime) -> datetime:
    if timestamp.tzinfo:
        timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
        logger.debug(f"    -> Converted to UTC: {timestamp}")

    return timestamp


def sort_dict(d: dict[str | None, int] | dict[str, int]) -> list[tuple[str | None, int]]:
    alpha_key = lambda kv: (kv[0] or '').lower()

    try:
        sort_key = alpha_key if args.sort_alphabetical else lambda kv: [-kv[1], alpha_key(kv)]
        return sorted(d.items(), key=sort_key)
    except TypeError as e:
        alpha_key = lambda kv: kv[0] or ''
        return sorted(d.items(), key=lambda kv: f"Z{alpha_key(kv)}" if '.' in (kv[0] or '') else alpha_key(kv))


def uniquify(_list: list[T]) -> list[T]:
    return list(set(_list))
