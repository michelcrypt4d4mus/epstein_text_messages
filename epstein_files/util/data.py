import itertools
import re
from typing import TypeVar

MULTINEWLINE_REGEX = re.compile(r"\n{2,}")

T = TypeVar('T')


def collapse_newlines(text: str) -> str:
    return MULTINEWLINE_REGEX.sub('\n\n', text)


def flatten(_list: list[list[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(_list))


def get_dict_key_by_value(_dict: dict, value):
    """Inverse of the usual dict operation."""
    return list(_dict.keys())[list(_dict.values()).index(value)]


def patternize(_pattern: str | re.Pattern):
    return _pattern if isinstance(_pattern, re.Pattern) else re.compile(rf"({_pattern})", re.IGNORECASE)
