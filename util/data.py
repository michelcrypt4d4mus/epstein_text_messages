import itertools
import re
from typing import TypeVar

T = TypeVar('T')


def flatten(_list: list[list[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(_list))


def get_dict_key_by_value(_dict: dict, value):
    """Inverse of the usual dict operation."""
    return list(_dict.keys())[list(_dict.values()).index(value)]


def patternize(_pattern: str | re.Pattern):
    return _pattern if isinstance(_pattern, re.Pattern) else re.compile(rf"({_pattern})", re.IGNORECASE)
