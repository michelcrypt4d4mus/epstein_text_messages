"""
The values in the enums match the suffixes of constants.py variables whose names
take the form 'OTHER_FILES_[enum_value]'.
"""
from enum import StrEnum, auto
from itertools import chain
from typing import Type

from epstein_files.util.constant.strings import *

DEFAULT_CATEGORY_STYLE = 'wheat4'

class CategoryEnum(StrEnum):
    pass

class Interesting(StrEnum):
    CRYPTO = auto()
    LETTER = auto()
    MONEY = auto()
    REPUTATION = auto()
    RESUMÉ = auto()
    SOCIAL = auto()
    TEXT_MSG = auto()

class Neutral(StrEnum):
    BUSINESS = auto()
    FINANCE = auto()
    FLIGHT_LOG = auto()
    LEGAL = auto()
    MISC = auto()
    PRESSER = auto()
    SKYPE_LOG = auto()

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
    Interesting.TEXT_MSG: TECH_BRO,
    Neutral.LEGAL: LAWYER,
    Neutral.SKYPE_LOG: TECH_BRO,
    Uninteresting.ARTICLE: JOURNALIST,
    Uninteresting.BOOK: JOURNALIST,
    Uninteresting.CONFERENCE: ACADEMIA,  # TODO: this maps to f"{get_style_for_category(ACADEMIA)} dim"
    Uninteresting.POLITICS: LOBBYIST,
    Uninteresting.PROPERTY: BUSINESS,
    Uninteresting.TWEET: Interesting.SOCIAL,
}

CATEGORY_STYLES = {
    Interesting.LETTER: 'medium_orchid1',
    Interesting.RESUMÉ: 'deep_pink4',
    Interesting.SOCIAL: 'yellow1',
    Neutral.FLIGHT_LOG: 'cyan',
    Neutral.MISC: 'deep_pink3',
    Neutral.PRESSER: 'sandy_brown',
    Uninteresting.JSON: 'dark_red',
    Uninteresting.PHONE_BILL: 'cyan',
}

# These are the categories we expect to see as OTHER_FILES_[category] variables for in constants.py
CONSTANT_CATEGORIES = [
    c for c in Category if c not in [
        Neutral.BUSINESS,
        Neutral.PRESSER,
        Uninteresting.JSON,
    ]
]


is_interesting = lambda category: is_in_enum(category, Interesting)
is_neutral = lambda category: is_in_enum(category, Neutral)
is_uninteresting = lambda category: is_in_enum(category, Uninteresting)


def is_category(s: str) -> bool:
    return any(fxn(s) for fxn in [is_interesting, is_neutral, is_uninteresting])


def is_in_enum(category: str, e: Type[StrEnum]) -> bool:
    return bool(next((c for c in e if c == category), False))
