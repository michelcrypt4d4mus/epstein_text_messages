import re
from typing import Literal


# categories
ACADEMIA = 'academia'
ARTS = 'arts'
ARTICLE = 'article'
BOOK = 'book'
BUSINESS = 'business'
CONFERENCE = 'conference'
CRYPTO = 'crypto'
FINANCE = 'finance'
FRIEND = 'friend'
FLIGHT_LOG = 'flight log'
JOURNALIST = 'journalist'
JUNK = 'junk'
LEGAL = 'legal'
LOBBYIST = 'lobbyist'
POLITICS = 'politics'
PROPERTY = 'property'
PUBLICIST = 'publicist'
REPUTATION = 'reputation'
SKYPE_LOG = 'Skype log'
SOCIAL = 'social'

# Locations
PALM_BEACH = 'Palm Beach'
VIRGIN_ISLANDS = 'Virgin Islands'

# Site types
EMAIL = 'email'
TEXT_MESSAGE = 'text message'
SiteType = Literal['email', 'text message']

# Styles
DEFAULT_NAME_STYLE = 'grey23'
TIMESTAMP_STYLE = 'turquoise4'
TIMESTAMP_DIM = f"turquoise4 dim"

# Misc
AUTHOR = 'author'
DEFAULT = 'default'
EFTA_PREFIX = 'EFTA'
HOUSE_OVERSIGHT_PREFIX = 'HOUSE_OVERSIGHT_'
JSON = 'json'
NA = 'n/a'
REDACTED = '<REDACTED>'
QUESTION_MARKS = '(???)'

# Document subclass names (this sucks)
DOCUMENT_CLASS = 'Document'
DOJ_FILE_CLASS = 'DojFile'
EMAIL_CLASS = 'Email'
JSON_FILE_CLASS = 'JsonFile'
MESSENGER_LOG_CLASS = 'MessengerLog'
OTHER_FILE_CLASS = 'OtherFile'

# Whitespace
INDENT = '    '
INDENT_NEWLINE = f'\n{INDENT}'
INDENTED_JOIN = f',{INDENT_NEWLINE}'

# Regexes
DOJ_FILE_STEM_REGEX = re.compile(fr"{EFTA_PREFIX}\d{{8}}")
DOJ_FILE_NAME_REGEX = re.compile(fr"{DOJ_FILE_STEM_REGEX.pattern}(\.txt)?")
HOUSE_OVERSIGHT_NOV_2025_ID_REGEX = re.compile(r"\d{6}(_\d{1,2})?")
HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_PREFIX}({HOUSE_OVERSIGHT_NOV_2025_ID_REGEX.pattern})")
HOUSE_OVERSIGHT_NOV_2025_FILE_NAME_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX.pattern}(\.txt(\.json)?)?")
QUESTION_MARKS_REGEX = re.compile(fr' {re.escape(QUESTION_MARKS)}$')
