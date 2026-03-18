import re
from typing import Literal

# Types
OcrRepair = dict[str | re.Pattern, str]
PartialName = Literal['both', 'first', 'last']

# Categories
ACADEMIA = 'academia'
ARTS = 'arts'
BUSINESS = 'business'
FRIEND = 'friend'
JOURNALIST = 'journalist'
LAWYER = 'lawyer'
LOBBYIST = 'lobbyist'
MIDEAST = 'mideast'
PUBLICIST = 'publicist'
REAL_ESTATE = 'real estate'
REPUTATION = 'reputation'
REPUTATION_MGMT = f'{REPUTATION} management'
TECH_BRO = 'tech'

# Locations
PALM_BEACH = 'Palm Beach'
VIRGIN_ISLANDS = 'Virgin Islands'

# Highlighter
HIGHLIGHTED_QUOTE = 'highlighted_quote'
REGEX_STYLE_PREFIX = 'regex'

# Styles
ALT_LINK_STYLE = 'white dim'
ARCHIVE_LINK_COLOR = 'slate_blue3'
ARCHIVE_LINK_UNDERLINE = f"{ARCHIVE_LINK_COLOR} underline"
ARCHIVE_ALT_LINK_STYLE = 'medium_purple4 italic'  # "(raw files)" link
AUX_SITE_LINK_STYLE = 'dark_orange3'
DEFAULT_NAME_STYLE = 'grey23'
EPSTEIN_COLOR = 'blue1'
EXCERPT_STYLE = 'italic cornsilk1'
INFO_STYLE = 'gray50 italic'
SUBHEADER_STYLE = 'dim gray54 italic'
TEXT_LINK = 'text_link'
TIMESTAMP_STYLE = 'turquoise4'
TIMESTAMP_DIM = f"turquoise4 dim"
VICTIM_LAWYER = 'victim lawyer'

# File IDs
LEON_BLACK_EMAIL_ID = '023208'

# Misc
APPEARS_IN = 'appears in'
ARTICLE_DRAFT = 'draft of an article about'
AUTHOR = 'author'
CHRONOLOGICAL = 'chronological'
DEFAULT = 'default'
EMAIL = 'email'
JEE = 'JEE'
JSON = 'json'
LAW_ENFORCEMENT = 'law enforcement'
NA = 'n/a'
REDACTED = '<REDACTED>'
QUESTION_MARKS = '(???)'
SCREENSHOT = 'screenshot of'
TEXT_MESSAGE = 'text message'
TRANSLATION = 'translation of'
VICTIM_DIARY = 'victim diary'
WIKIPEDIA = 'WIKIPEDIA'

# CLI args
SUPPRESS_OUTPUT = '--suppress-output'

# Document subclass names (this sucks)
DOCUMENT_CLASS = 'Document'
DOJ_FILE_CLASS = 'DojFile'
EMAIL_CLASS = 'Email'
JSON_FILE_CLASS = 'JsonFile'
MESSENGER_LOG_CLASS = 'MessengerLog'
OTHER_FILE_CLASS = 'OtherFile'

# Law
CVRA = "Crime Victims' Rights Act [CVRA]"
JASTA = 'JASTA'
JASTA_FULL = f"{JASTA} (Justice Against Sponsors of Terrorism Act)"
MINOR_VICTIM = 'minor victim'

# Organizations
BROCKMAN_INC = 'Brockman, Inc.'
HARVARD = 'Harvard'
HARVARD_POETRY = f'{HARVARD} poetry stuff from Lisa New'  # TODO: name be here?
PALM_BEACH_CODE_ENFORCEMENT = f'{PALM_BEACH} Code Enforcement'
PALM_BEACH_PROPERTY_INFO = f"{PALM_BEACH} property info"
PALM_BEACH_TSV = f"TSV of {PALM_BEACH} property"
PALM_BEACH_WATER_COMMITTEE = f'{PALM_BEACH} Water Committee'
UN_GENERAL_ASSEMBLY = '67th U.N. General Assembly'

# Tranches
DOJ_2026_TRANCHE = '2026 DOJ tranche'
HOUSE_OVERSIGHT_TRANCHE = '2025 Oversight tranche'
EPSTEIN_FILES_NOV_2025 = 'epstein_files_nov_2025'

# Regexes / file names
EFTA_PREFIX = 'EFTA'
HOUSE_OVERSIGHT_PREFIX = 'HOUSE_OVERSIGHT_'
DOJ_DATASET_ID_REGEX = re.compile(r"(?:epstein_dataset_|DataSet )(\d+)")
DOJ_FILE_STEM_REGEX = re.compile(fr"({EFTA_PREFIX}\d{{8}}(_\d{{1,3}})?)")
DOJ_FILE_NAME_REGEX = re.compile(fr"{DOJ_FILE_STEM_REGEX.pattern}(\.txt)?")
HOUSE_OVERSIGHT_NOV_2025_ID_REGEX = re.compile(r"(\d{6}(_\d{1,3})?)")
HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_PREFIX}{HOUSE_OVERSIGHT_NOV_2025_ID_REGEX.pattern}")
HOUSE_OVERSIGHT_NOV_2025_FILE_NAME_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX.pattern}(\.txt(\.json)?)?")
LOCAL_EXTRACT_REGEX = re.compile(r"_\d{1,2}$")
QUESTION_MARKS_REGEX = re.compile(fr' {re.escape(QUESTION_MARKS)}$')

# Other regexes
AMPERSAND_CHAR_GROUP = r"[®©@ae]"  # Chars the OCR messes up when scanning '@'
CASE_ID_REGEX = re.compile(r"Case\s+(Number:\s+)?\d:\d{2}-[a-z]{2}-\d{5}-[A-Z]{3}")

# Decorative
LEFT_ARROWS = '⇚ ⇠ ⇷ ⟵ ⇜ ⇽ ⬰ ⬲'
RIGHT_ARROWS = '↦ ↠ ➔ ➤ ➦ ➱ ➪ ➾'
LINES = '-﹊﹌﹉﹏﹎＿'

# Whitespace
INDENT = '    '
INDENT_NEWLINE = f'\n{INDENT}'
INDENTED_JOIN = f',{INDENT_NEWLINE}'

WEEKDAYS = 'Sunday Monday Tuesday Wednesday Thursday Friday Saturday'.split()
MONTHS = 'January February March April May June July August September October November December'.split()

STATES_PIPE_DELIMITED = """
AL|Alabama
AK|Alaska
AZ|Arizona
AR|Arkansas
CA|California
CO|Colorado
CT|Connecticut
DE|Delaware
FL|Florida
GA|Georgia
HI|Hawaii
ID|Idaho
IL|Illinois
IN|Indiana
IA|Iowa
KS|Kansas
KY|Kentucky
LA|Louisiana
ME|Maine
MD|Maryland
MA|Massachusetts
MI|Michigan
MN|Minnesota
MS|Mississippi
MO|Missouri
MT|Montana
NE|Nebraska
NY|New York
NV|Nevada
NH|New Hampshire
NJ|New Jersey
NM|New Mexico
NC|North Carolina
ND|North Dakota
OH|Ohio
OK|Oklahoma
OR|Oregon
PA|Pennsylvania
RI|Rhode Island
SC|South Carolina
SD|South Dakota
TN|Tennessee
TX|Texas
UT|Utah
VT|Vermont
VA|Virginia
WA|Washington
WV|West Virginia
WI|Wisconsin
WY|Wyoming
""".strip()

OTHER_US_DELIMITED = """
DC|District of Columbia
AS|American Samoa
GU|Guam
MP|Northern Mariana Islands
PR|Puerto Rico
UM|United States Minor Outlying Islands
VI|Virgin Islands, U.S.
""".strip()

STATE_CODES = {
    row.split('|')[0]: row.split('|')[1]
    for row in STATES_PIPE_DELIMITED.split('\n')
}

# some states excluded for pattern matching reasons re: important locations or names
STATE_NAME_PATTERNS = [
    f"{state}n?" if state.endswith('a') else state
    for state in STATE_CODES.values()
    if state not in ['Arizon', 'Florida', 'New York', 'Texas', 'Virginia', 'Washington']
]

RUSSIAN_WEEKDAYS = [
    'понедельник',
    'вторник', 'Вторник',
    'среда',
    'четверг', 'Четверг',
    'пятница',
    'суббота',
    'воскресенье',
]

RUSSIAN_ON = 'в'
