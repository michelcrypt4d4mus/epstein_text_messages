"""
Constants and methods for identifying people in email headers.
"""
import re

from epstein_files.output.highlight_config import HIGHLIGHTED_CONTACTS
from epstein_files.people.contact import Contact, organization
from epstein_files.people.names import *
from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.helpers.data_helpers import escape_single_quotes, flatten
from epstein_files.util.logging import logger

BAD_EMAILER_REGEX = re.compile(r'^(>|11111111)|agreed|ok(?!asha)|sexy|re:|fwd:|LIMITED PARTNERS|Multiple Senders|((sent|attachments|subject|importance).*|.*(january|201\d|hysterical|i have|image0|so that people|article 1.?|PROSPECTIVE INVESTORS|momminnemummin|These conspiracy theories|your state|undisclosed|www\.theguardian|talk in|it was a|what do|cc:|call (back|me)|afiaata|[IM]{4,}).*)$', re.IGNORECASE)
BAD_NAME_CHARS_REGEX = re.compile(r"[\"'\[\]*><•=()‹?]")
TIME_REGEX = re.compile(r'^((\d{1,2}/\d{1,2}/\d{2,4}|Thursday|Monday|Tuesday|Wednesday|Friday|Saturday|Sunday)|\d{4} ).*')

# Unhighlighted / uncategorized emailers we don't know much about but need regexes to identify
ADDITIONAL_CONTACTS = [
    # Custom regex
    Contact('BS Stern', emailer_pattern=r"BS Ste(m|rn)"),
    Contact(INTELLIGENCE_SQUARED, emailer_pattern=r"intelligence\s*squared"),
    Contact('Matthew Schafer', emailer_pattern=r"matthew\.?schafer?"),
    Contact(MICHAEL_BUCHHOLTZ, emailer_pattern=r"Michael.*Buchholtz"),
    Contact(SAMUEL_LEFF, emailer_pattern=r"Sam(uel)?(/Walli)? Leff"),
    Contact(THANU_BOONYAWATANA, emailer_pattern=r"Thanu (BOONYAWATANA|Cnx)"),
    # No custom regex
    Contact('Amanda Kirby'),
    Contact('Anne Boyles', match_partial=None),
    Contact('Ariane Dwyer'),
    Contact('Brittany Henderson'),
    Contact('Danny Goldberg', match_partial=None),
    Contact('Jeff Pagliuca'),
    Contact(JOHN_PAGE, match_partial=None),
    Contact('Julie Shample'),
    Contact('Kathleen Ruderman'),
    Contact('Kevin Bright', match_partial=None),
    Contact('Larry Cohen', match_partial=None),
    Contact('Lawrence Delson'),
    Contact('Michael Simmons', match_partial=None),
    Contact('middle.east.update@hotmail.com'),
    Contact('Nancy Cain'),
    Contact('Nancy Portland', match_partial=None),
    Contact(OLIVER_GOODENOUGH),
    Contact('Peter Green', match_partial=None),
    Contact('Sarah Mapes'),
]

SUPPRESS_LOGS_FOR_AUTHORS = [
    'Multiple Senders Multiple Senders',
    'Undisclosed recipients:',
    'undisclosed-recipients:',
]

# Collect all regexes and contacts
ALL_CONTACTS = [c for c in HIGHLIGHTED_CONTACTS if c.is_emailer] + ADDITIONAL_CONTACTS
CONTACTS_DICT = {c.name: c for c in ALL_CONTACTS}
EMAILER_ID_REGEXES = {c.name: c.emailer_regex for c in ALL_CONTACTS}


# Dictionary of string that usually signify an identity if present in email body
UNIQUE_IDENTIFIERS = {
    'tupos & abbrvtns': CONTACTS_DICT[LINDA_STONE],
    'Typos, misspellings courtesy of iPhone': CONTACTS_DICT[LINDA_STONE],
}

for contact in ALL_CONTACTS:
    for email_address in contact.email_addresses:
        UNIQUE_IDENTIFIERS[email_address] = contact


def cleanup_str(s: str) -> str:
    return BAD_NAME_CHARS_REGEX.sub('', s.replace(REDACTED, '')).strip().strip('_').strip()


def extract_emailer_names(emailer_str: str) -> list[Name]:
    """Return a list of people's names found in `emailer_str` (email author or recipients field)."""
    raw_names = emailer_str.split(';')
    emailer_str = cleanup_str(emailer_str)

    if len(emailer_str) == 0:
        return []
    elif raw_names == [REDACTED] or raw_names == [UNKNOWN]:
        return [None]
    elif emailer_str.lower() in ['j', 'jeffrey']:
        return [JEFFREY_EPSTEIN]
    elif emailer_str.lower() in ['sa', 's a']:
        return [SHAHER_ABDULHAK_BESHER]

    names_found: list[Name] = [name for name, regex in EMAILER_ID_REGEXES.items() if regex.search(emailer_str)]

    if len(emailer_str) <= 2 or BAD_EMAILER_REGEX.match(emailer_str) or TIME_REGEX.match(emailer_str):
        if len(names_found) == 0 and emailer_str not in SUPPRESS_LOGS_FOR_AUTHORS:
            logger.warning(f"No emailer found in '{escape_single_quotes(emailer_str)}'")
        else:
            logger.info(f"Extracted {len(names_found)} names from semi-invalid '{emailer_str}': {names_found}...")

        return names_found


    names_found = [reverse_first_and_last_names(name) for name in (names_found or [emailer_str])]
    logger.debug(f"names_found in '{emailer_str}': {names_found}")
    return names_found
