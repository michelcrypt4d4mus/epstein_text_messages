import re

# Categories
ACADEMIA = 'academia'
ARTS = 'arts'
BUSINESS = 'business'
FRIEND = 'friend'
JOURNALIST = 'journalist'
JUNK = 'junk'
LAWYER = 'lawyer'
LOBBYIST = 'lobbyist'
MIDEAST = 'mideast'
PUBLICIST = 'publicist'
REPUTATION = 'reputation'
REPUTATION_MGMT = f'{REPUTATION} management'
TECH_BRO = 'tech bro'

# Locations
PALM_BEACH = 'Palm Beach'
VIRGIN_ISLANDS = 'Virgin Islands'

# Styles
ALT_LINK_STYLE = 'white dim'
ARCHIVE_LINK_COLOR = 'slate_blue3'
ARCHIVE_LINK_UNDERLINE = f"{ARCHIVE_LINK_COLOR} underline"
ARCHIVE_ALT_LINK_STYLE = 'medium_purple4 italic'  # "(raw files)" link
AUX_SITE_LINK_STYLE = 'dark_orange3'
TEXT_LINK = 'text_link'
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
EMAIL = 'email'
JSON = 'json'
NA = 'n/a'
REDACTED = '<REDACTED>'
QUESTION_MARKS = '(???)'
TEXT_MESSAGE = 'text message'

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
DOJ_FILE_STEM_REGEX = re.compile(fr"{EFTA_PREFIX}\d{{8}}")
DOJ_FILE_NAME_REGEX = re.compile(fr"{DOJ_FILE_STEM_REGEX.pattern}(\.txt)?")
HOUSE_OVERSIGHT_NOV_2025_ID_REGEX = re.compile(r"\d{6}(_\d{1,2})?")
HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_PREFIX}({HOUSE_OVERSIGHT_NOV_2025_ID_REGEX.pattern})")
HOUSE_OVERSIGHT_NOV_2025_FILE_NAME_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX.pattern}(\.txt(\.json)?)?")
LOCAL_EXTRACT_REGEX = re.compile(r"_\d$")
QUESTION_MARKS_REGEX = re.compile(fr' {re.escape(QUESTION_MARKS)}$')

# Decorative
LEFT_ARROWS = '⇚ ⇠ ⇷ ⟵ ⇜ ⇽ ⬰ ⬲'
RIGHT_ARROWS = '↦ ↠ ➔ ➤ ➦ ➱ ➪ ➾'

# Whitespace
INDENT = '    '
INDENT_NEWLINE = f'\n{INDENT}'
INDENTED_JOIN = f',{INDENT_NEWLINE}'
