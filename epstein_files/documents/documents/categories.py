"""
The values in the enums match the suffixes of constants.py variables whose names
take the form 'OTHER_FILES_[enum_value]'.
"""
from enum import StrEnum, auto
from itertools import chain
from typing import Type

from epstein_files.util.constant.strings import *

DEFAULT_CATEGORY_STYLE = 'wheat4'
SOCIAL_STYLE = 'khaki3'
RUSSIAN_GIRL = 'russian girl'

class Interesting(StrEnum):
    CRYPTO = auto()
    DIARY = auto()
    GIRLS = auto()
    MONEY = auto()
    REPUTATION = auto()
    SOCIAL = auto()

class Neutral(StrEnum):
    BUSINESS = auto()
    DEPOSITION = auto()
    FINANCE = auto()
    FLIGHT_LOG = auto()
    GOVERNMENT = auto()
    LEGAL = auto()
    MISC = auto()
    PRESSER = auto()
    RESUMÉ = auto()

class Uninteresting(StrEnum):
    ACADEMIA = auto()
    ARTICLE = auto()
    ARTS = auto()
    BOOK = auto()
    CONFERENCE = auto()
    JSON = auto()
    JUNK = auto()
    POLITICS = auto()
    PHONE_BILL = auto()
    PROPERTY = auto()
    TWEET = auto()

# Enum concat from here: https://stackoverflow.com/questions/71527981/combine-two-or-more-enumeration-classes-in-order-to-have-more-levels-access
class Category(StrEnum):
    _ignore_ = 'member cls'
    cls = vars()

    for member in chain(list(Interesting), list(Neutral), list(Uninteresting)):
        cls[member.name] = member.value

    def __str__(self):
        return str(self.value)


# These categories map to highlighted group labels for the purposes of coloring
CATEGORY_STYLE_MAPPING = {
    Interesting.MONEY: Neutral.FINANCE,
    Interesting.REPUTATION: PUBLICIST,
    Neutral.DEPOSITION: VICTIM_LAWYER,
    Neutral.LEGAL: LAWYER,
    Neutral.PRESSER: PUBLICIST,
    Uninteresting.ARTICLE: JOURNALIST,
    Uninteresting.BOOK: JOURNALIST,
    Uninteresting.CONFERENCE: ACADEMIA,
    Uninteresting.POLITICS: LOBBYIST,
    Uninteresting.PROPERTY: REAL_ESTATE,
}

CATEGORY_STYLES = {
    'letter': 'plum4',
    Interesting.SOCIAL: SOCIAL_STYLE,
    Neutral.FLIGHT_LOG: EPSTEIN_COLOR,
    Neutral.MISC: 'navajo_white1',
    Neutral.RESUMÉ: 'deep_pink4',
    Uninteresting.JSON: 'dark_red',
    Uninteresting.PHONE_BILL: 'slate_blue3',
    Uninteresting.TWEET: SOCIAL_STYLE,
}


is_interesting = lambda category: _is_in_enum(category, Interesting)
is_neutral = lambda category: _is_in_enum(category, Neutral)
is_uninteresting = lambda category: _is_in_enum(category, Uninteresting)


def is_category(s: str) -> bool:
    return any(fxn(s) for fxn in [is_interesting, is_neutral, is_uninteresting])


def sort_categories(categories: list[str]) -> list[str]:
    """Sort by interestingness + alphabetical."""
    def sort_key(category) -> tuple[int, str]:
        if is_interesting(category):
            value = 10
        elif category == RUSSIAN_GIRL:
            value = 8
        elif category == TECH_BRO:
            value = 6
        elif (category or Uninteresting.JUNK) == Uninteresting.JUNK:
            value = -5
        elif is_neutral(category):
            value = 5
        elif is_uninteresting(category):
            value = 0
        else:
            value = 2

        return (-1 * value, category.lower())

    return sorted(categories, key=sort_key)


def _is_in_enum(category: str, e: Type[StrEnum]) -> bool:
    return bool(next((c for c in e if c == category), False))
