import itertools
import re
from typing import TypeVar

MULTINEWLINE_REGEX = re.compile(r"\n{2,}")

T = TypeVar('T')


def collapse_newlines(text: str) -> str:
    return MULTINEWLINE_REGEX.sub('\n\n', text)


def dict_sets_to_lists(d: dict[str, set]) -> dict[str, list]:
    return {k: sorted(list(v)) for k, v in d.items()}


def flatten(_list: list[list[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(_list))


def patternize(_pattern: str | re.Pattern):
    return _pattern if isinstance(_pattern, re.Pattern) else re.compile(rf"({_pattern})", re.IGNORECASE)
