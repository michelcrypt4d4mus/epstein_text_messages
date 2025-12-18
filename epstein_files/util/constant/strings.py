from typing import Literal


# Document subclass names (this sucks)
DOCUMENT_CLASS = 'Document'
EMAIL_CLASS = 'Email'
MESSENGER_LOG_CLASS = 'MessengerLog'
OTHER_FILE_CLASS = 'OtherFile'

# Misc
AUTHOR = 'author'
DEFAULT = 'default'
EVERYONE = 'everyone'
HOUSE_OVERSIGHT_PREFIX = 'HOUSE_OVERSIGHT_'
NA = 'n/a'
REDACTED = '<REDACTED>'
URL_SIGNIFIERS = ['gclid', 'htm', 'ref=', 'utm']

# Site types
EMAIL = 'email'
TEXT_MESSAGE = 'text message'
SiteType = Literal['email', 'text message']

# Styles
OTHER_SITE_LINK_STYLE = 'dark_goldenrod'
PHONE_NUMBER_STYLE = 'bright_green'
TIMESTAMP_STYLE = 'dark_cyan'
TIMESTAMP_DIM = f"{TIMESTAMP_STYLE} dim"
