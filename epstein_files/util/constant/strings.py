import re
from typing import Literal


# Document subclass names (this sucks)
DOCUMENT_CLASS = 'Document'
EMAIL_CLASS = 'Email'
JSON_FILE_CLASS = 'JsonFile'
MESSENGER_LOG_CLASS = 'MessengerLog'
OTHER_FILE_CLASS = 'OtherFile'

# Publications
BBC = 'BBC'
BLOOMBERG = 'Bloomberg'
CHINA_DAILY = "China Daily"
DAILY_MAIL = 'Daily Mail'
DAILY_TELEGRAPH = "Daily Telegraph"
LA_TIMES = 'LA Times'
MIAMI_HERALD = 'Miami Herald'
NYT_ARTICLE = 'NYT article about'
NYT_COLUMN = 'NYT column about'
THE_REAL_DEAL = 'The Real Deal'
WAPO = 'WaPo'

# Site types
EMAIL = 'email'
TEXT_MESSAGE = 'text message'
SiteType = Literal['email', 'text message']

# Styles
OTHER_SITE_LINK_STYLE = 'dark_goldenrod'
TIMESTAMP_STYLE = 'turquoise4'
TIMESTAMP_DIM = f"turquoise4 dim"

# Misc
AUTHOR = 'author'
DEFAULT = 'default'
EVERYONE = 'everyone'
FIRST_FEW_LINES = 'First Few Lines'
HOUSE_OVERSIGHT_PREFIX = 'HOUSE_OVERSIGHT_'
NA = 'n/a'
REDACTED = '<REDACTED>'
URL_SIGNIFIERS = ['gclid', 'htm', 'ref=', 'utm']
QUESTION_MARKS = '(???)'

# Regexes
FILE_STEM_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_PREFIX}(\d{{6}})")
FILE_NAME_REGEX = re.compile(fr"{FILE_STEM_REGEX.pattern}(_\d{{1,2}})?(\.txt(\.json)?)?")
QUESTION_MARKS_REGEX = re.compile(fr' {re.escape(QUESTION_MARKS)}$')


remove_question_marks = lambda name: QUESTION_MARKS_REGEX.sub('', name)
