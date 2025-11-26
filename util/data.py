import itertools
import re
from typing import TypeVar, Type

T = TypeVar('T')


def flatten(_list: list[list[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(_list))


def patternize(_pattern: str | re.Pattern):
    return _pattern if isinstance(_pattern, re.Pattern) else re.compile(rf"{_pattern}", re.IGNORECASE)
