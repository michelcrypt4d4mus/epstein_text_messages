from enum import auto, StrEnum

from epstein_files.util.constant.strings import *


# TODO: fill in other categories to the enum
class Category(StrEnum):
    PHONE_BILL = auto()


# These category names correspond to OTHER_FILES_[CATEGORY] vars in constants.py
INTERESTING_CATEGORIES = [
    CRYPTO,
    LETTER,
    MONEY,
    REPUTATION,
    RESUME,
    TEXT_MSG,
]

NEUTRAL_CATEGORIES = [
    FINANCE,
    LEGAL,
    MISC,
]

UNINTERESTING_CATEGORIES = [
    Category.PHONE_BILL,
    ACADEMIA,
    ARTICLE,
    ARTS,
    BOOK,
    CONFERENCE,
    JUNK,
    POLITICS,
    PROPERTY,
    SOCIAL,
]

CATEGORIES_THAT_ARE_NOT_VARNAME_SUFFIXES = [
    PRESS_RELEASE,
    SKYPE_LOG,
]

CATEGORY_STYLE_MAPPING = {
    ARTICLE: JOURNALIST,
    BOOK: JOURNALIST,
    LEGAL: LAWYER,
    MONEY: FINANCE,
    POLITICS: LOBBYIST,
    PROPERTY: BUSINESS,
    REPUTATION: PUBLICIST,
    TWEET: SOCIAL,
}


CATEGORY_STYLES = {
    JSON: 'dark_red',
    'letter': 'medium_orchid1'
}
