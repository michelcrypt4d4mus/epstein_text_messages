"""
Helpers for dealing with various kinds of data.
"""
import itertools
import re
from collections import Counter
from copy import copy
from datetime import datetime, timezone
from dateutil import tz
from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence, TypeVar

from epstein_files.people import names
from epstein_files.util.env import args
from epstein_files.util.helpers.string_helper import timestamp_str
from epstein_files.util.logging import logger

ISO_DATE_REGEX = re.compile(r'\d{4}-\d{2}(-\d{2})?')
CONSTANT_VAR_REGEX = re.compile(r"^[A-Z_]+$")
ALL_NAMES = [v for k, v in vars(names).items() if isinstance(v, str) and CONSTANT_VAR_REGEX.match(k)]

AMERICAN_DATE_FORMAT = r"%m/%d/%y %I:%M:%S %p"
AMERICAN_TIME_REGEX = re.compile(r"(\d{1,2}/\d{1,2}/\d{2,4}\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)")
PACIFIC_TZ = tz.gettz("America/Los_Angeles")
TIMEZONE_INFO = {"PDT": PACIFIC_TZ, "PST": PACIFIC_TZ}  # Suppresses annoying warnings from parse() calls

all_elements_same = lambda _list: len(_list) == 0 or all(x == _list[0] for x in _list)
coerce_utc = lambda dt: coerce_utc_strict(dt) if dt else None
date_str = lambda dt: dt.isoformat()[0:10] if dt else None
dict_key_list = lambda d: [k for k in d.keys()]
escape_double_quotes = lambda text: text.replace('"', r'\"')
escape_single_quotes = lambda text: text.replace("'", r"\'")
days_between = lambda dt1, dt2: (dt2 - dt1).days + 1
days_between_abs = lambda dt1, dt2: abs(days_between(dt1, dt2))
days_between_str = lambda dt1, dt2: f"{days_between(dt1, dt2)} day" + ('s' if days_between(dt1, dt2) > 1 else '')
uniquify = lambda _list: list(set(_list))

T = TypeVar('T')
U = TypeVar('U')


def add_constant(sequence: Sequence[int], constant: float | int) -> list[int | float]:
    return [s + constant for s in sequence]


def add_lists(arr1: list[int | float] | None, arr2: list[int | float] | None) -> list[int | float]:
    if arr1 is None and arr2:
        return arr2
    elif arr2 is None:
        return arr1
    else:
        return [_val + arr2[i] for i, _val in enumerate(arr1)]


def build_name_lookup(objs: list[T]) -> dict[names.Name, T]:
    """Dict of objects keyed by `name` property."""
    return {c.name: c for c in objs}


def coerce_utc_strict(dt: datetime) -> datetime:
    if not dt:
        return None

    old_dt_str = timestamp_str(dt)

    if not dt.tzinfo:
        dt = dt.replace(tzinfo=tz.UTC)

    dt = dt.astimezone(tz.UTC)
    dt_str = timestamp_str(dt)

    if old_dt_str != dt_str:
        logger.debug(f"Coerced timestamp '{old_dt_str}' to '{dt_str}' (ISO: '{dt.isoformat()}')")

    return dt


def constantize_names(s: str) -> str:
    """Replace occurences of 'Jeffrey Epstein' with '{JEFFREY_EPSTEIN}' etc."""
    for name in ALL_NAMES:
        s = s.replace(name, f"{{{names.constantize_name(name)}}}")

    return s


def count_dupes(objs: Sequence[T]) -> dict[T, int]:
    """Return a dict with only the objects that appear more than once in `objs` and their counts."""
    return {k: v for k, v in Counter(objs).items() if v > 1}


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


def groupby(objs: Sequence[T], key: Callable[[T], U]) -> dict[U, list[T]]:
    """itertools.groupby() has annoying return type."""
    return {k: list(v) for k, v in itertools.groupby(objs, key=key)}


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


def sort_dict(d: dict[str | None, int] | dict[str, int]) -> list[tuple[str | None, int]]:
    alpha_key = lambda kv: (kv[0] or '').lower()

    try:
        sort_key = alpha_key if args.sort_alphabetical else lambda kv: [-kv[1], alpha_key(kv)]
        return sorted(d.items(), key=sort_key)
    except TypeError as e:
        alpha_key = lambda kv: kv[0] or ''
        return sorted(d.items(), key=lambda kv: f"Z{alpha_key(kv)}" if '.' in (kv[0] or '') else alpha_key(kv))


def sort_dict_by_keys(d: Mapping[names.Name, T]) -> dict[names.Name, T]:
    return {k: d[k] for k in names.sort_names(dict_key_list(d))}


def update_truthy(old_dict: dict[str, T], new_dict: dict[str, T]) -> None:
    """Like dict update() but don't write keys with empty values."""
    for k, v in new_dict.items():
        if v:
            old_dict[k] = v


def uniq_sorted(_list: Sequence[T], reverse: bool = False) -> list[T]:
    return sorted(uniquify(_list), reverse=reverse)


def uniquify(_list: Sequence[T]) -> list[T]:
    return list(set(_list))


def warn_on_dupes(objs: Sequence[T]) -> dict[T, int]:
    """Same as count_dupes() but with a warning."""
    if (dupe_counts := count_dupes(objs)):
        dupes = uniq_sorted([dupe for dupe in dupe_counts.keys()])
        logger.error(f"Found {len(dupes)} dupes out of {len(objs)} objs:\n\n{dupe_counts}\n")
        logger.error(f"Raw dupes:\n\n" + ' '.join(dupes) + '\n')
        return dupe_counts
    else:
        return {}


def without_falsey(elements: Sequence[T | None]) -> list[T]:
    return [e for e in elements if e]
