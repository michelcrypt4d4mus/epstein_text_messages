import itertools
from typing import TypeVar, Type

T = TypeVar('T')


def flatten(_list: list[list[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(_list))
