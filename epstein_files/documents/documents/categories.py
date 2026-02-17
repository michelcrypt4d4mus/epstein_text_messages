"""
The values in the enums match the suffixes of constants.py variables whose names
take the form 'OTHER_FILES_[enum_value]'.
"""
from enum import auto, StrEnum
from itertools import chain
from typing import Type

from epstein_files.util.constant.strings import *


class Interesting(StrEnum):
    CRYPTO = auto()
    LETTER = auto()
    MONEY = auto()
    REPUTATION = auto()
    RESUME = auto()
    SOCIAL = auto()
    TEXT_MSG = auto()

class Neutral(StrEnum):
    FINANCE = auto()
    FLIGHT_LOG = auto()
    LEGAL = auto()
    MISC = auto()
    PRESS_RELEASE = auto()
    SKYPE_LOG = auto()
    TWEET = auto()

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

# Enum concat from here: https://stackoverflow.com/questions/71527981/combine-two-or-more-enumeration-classes-in-order-to-have-more-levels-access
class Category(StrEnum):
    _ignore_ = 'member cls'
    cls = vars()

    for member in chain(list(Interesting), list(Neutral), list(Uninteresting)):
        cls[member.name] = member.value

    def __str__(self):
        return str(self.value)

CATEGORY_STYLE_MAPPING = {
    Uninteresting.ARTICLE: JOURNALIST,
    Uninteresting.BOOK: JOURNALIST,
    Neutral.LEGAL: LAWYER,
    Interesting.MONEY: FINANCE,
    Uninteresting.POLITICS: LOBBYIST,
    Uninteresting.PROPERTY: BUSINESS,
    Interesting.REPUTATION: PUBLICIST,
    Neutral.TWEET: SOCIAL,
}

CATEGORY_STYLES = {
    Uninteresting.JSON: 'dark_red',
    Interesting.LETTER: 'medium_orchid1'
}

# These are the categories we expect to see as OTHER_FILES_[category] variables for in constants.py
CONSTANT_CATEGORIES = [c for c in Category if c not in [Uninteresting.JSON, Neutral.PRESS_RELEASE]]


is_interesting = lambda category: is_in_enum(category, Interesting)
is_neutral = lambda category: is_in_enum(category, Neutral)
is_uninteresting = lambda category: is_in_enum(category, Uninteresting)


def is_category(s: str) -> bool:
    return any(fxn(s) for fxn in [is_interesting, is_neutral, is_uninteresting])


def is_in_enum(category: str, e: Type[StrEnum]) -> bool:
    return bool(next((c for c in e if c == category), False))
