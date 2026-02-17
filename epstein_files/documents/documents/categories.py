from enum import auto, StrEnum

from epstein_files.util.constant.strings import *


# TODO: fill in other categories to the enum
class Category(StrEnum):
    PHONE_BILL = auto()


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
