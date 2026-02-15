import re
from typing import Literal

# Categories
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
LAWYER = 'lawyer'
LEGAL = 'legal'
LETTER = 'letter'
LOBBYIST = 'lobbyist'
MIDEAST = 'mideast'
MISC = 'misc'
MONEY = 'money'
POLITICS = 'politics'
PRESS_RELEASE = 'press release'
PROPERTY = 'property'
PUBLICIST = 'publicist'
REPUTATION = 'reputation'
REPUTATION_MGMT = f'{REPUTATION} management'
RESUME = 'resume'
# RESUME_ACCENTED = 'resumé'
SKYPE_LOG = 'skype log'
TEXT_MSG = 'text_msg'
TWEET = 'tweet'
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
SUBHEADER_STYLE = 'grey46'
TIMESTAMP_STYLE = 'turquoise4'
TIMESTAMP_DIM = f"turquoise4 dim"
# Highlighter
REGEX_STYLE_PREFIX = 'regex'

# Misc
APPEARS_IN = 'appears in'
AUTHOR = 'author'
DEFAULT = 'default'
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

# Law
CVRA = "Crime Victims' Rights Act [CVRA]"
JASTA = 'JASTA'

# Organizations
BROCKMAN_INC = 'Brockman, Inc.'
HARVARD = 'Harvard'
HARVARD_POETRY = f'{HARVARD} poetry stuff from Lisa New'  # TODO: name be here?
PALM_BEACH_CODE_ENFORCEMENT = f'{PALM_BEACH} Code Enforcement'
PALM_BEACH_PROPERTY_INFO = f"{PALM_BEACH} property info"
PALM_BEACH_TSV = f"TSV of {PALM_BEACH} property"
PALM_BEACH_WATER_COMMITTEE = f'{PALM_BEACH} Water Committee'
UN_GENERAL_ASSEMBLY = '67th U.N. General Assembly'

# Regexes / file names
EFTA_PREFIX = 'EFTA'
HOUSE_OVERSIGHT_PREFIX = 'HOUSE_OVERSIGHT_'
DOJ_FILE_STEM_REGEX = re.compile(fr"{EFTA_PREFIX}\d{{8}}")
DOJ_FILE_NAME_REGEX = re.compile(fr"{DOJ_FILE_STEM_REGEX.pattern}(\.txt)?")
HOUSE_OVERSIGHT_NOV_2025_ID_REGEX = re.compile(r"\d{6}(_\d{1,2})?")
HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_PREFIX}({HOUSE_OVERSIGHT_NOV_2025_ID_REGEX.pattern})")
HOUSE_OVERSIGHT_NOV_2025_FILE_NAME_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX.pattern}(\.txt(\.json)?)?")
QUESTION_MARKS_REGEX = re.compile(fr' {re.escape(QUESTION_MARKS)}$')
