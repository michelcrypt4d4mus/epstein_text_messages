import itertools
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import TypeVar

from epstein_files.util.constant import names
from epstein_files.util.env import args, logger

MULTINEWLINE_REGEX = re.compile(r"\n{2,}")
CONSTANT_VAR_REGEX = re.compile(r"^[A-Z_]+$")
ALL_NAMES = [v for k, v in vars(names).items() if isinstance(v, str) and CONSTANT_VAR_REGEX.match(k)]

T = TypeVar('T')


def collapse_newlines(text: str) -> str:
    return MULTINEWLINE_REGEX.sub('\n\n', text)


def dict_sets_to_lists(d: dict[str, set]) -> dict[str, list]:
    return {k: sorted(list(v)) for k, v in d.items()}


def flatten(_list: list[list[T]]) -> list[T]:
    return list(itertools.chain.from_iterable(_list))


def patternize(_pattern: str | re.Pattern):
    return _pattern if isinstance(_pattern, re.Pattern) else re.compile(rf"({_pattern})", re.IGNORECASE)


def sort_dict(d: dict[str | None, int]) -> list[tuple[str | None, int]]:
    sort_key = lambda e: (e[0] or '').lower() if args.sort_alphabetical else [-e[1], (e[0] or '').lower()]
    return sorted(d.items(), key=sort_key)


@dataclass
class Timer:
    started_at: float = field(default_factory=lambda: time.perf_counter())
    checkpoint_at: float = field(default_factory=lambda: time.perf_counter())

    def print_at_checkpoint(self, msg: str) -> None:
        logger.warning(f"{msg} in {self.seconds_since_checkpoint()}")
        self.checkpoint_at = time.perf_counter()

    def seconds_since_checkpoint(self) -> str:
        return f"{(time.perf_counter() - self.checkpoint_at):.2f} seconds"

    def seconds_since_start(self) -> str:
        return f"{(time.perf_counter() - self.started_at):.2f} seconds"


escape_double_quotes = lambda text: text.replace('"', r'\"')
escape_single_quotes = lambda text: text.replace("'", r"\'")
uniquify = lambda _list: list(set(_list))
