"""
Constants and methods for dentifying people in email headers.
"""
import re

from epstein_files.people.contact_info import Contact
from epstein_files.output.highlighted_names import HighlightedNames
from epstein_files.output.highlight_config import HIGHLIGHTED_NAMES
from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.helpers.data_helpers import escape_single_quotes, flatten
from epstein_files.util.logging import logger

BAD_EMAILER_REGEX = re.compile(r'^(>|11111111)|agreed|ok|sexy|re:|fwd:|Multiple Senders|((sent|attachments|subject|importance).*|.*(january|201\d|hysterical|i have|image0|so that people|article 1.?|momminnemummin|These conspiracy theories|your state|undisclosed|www\.theguardian|talk in|it was a|what do|cc:|call (back|me)|afiaata|[IM]{4,}).*)$', re.IGNORECASE)
BAD_NAME_CHARS_REGEX = re.compile(r"[\"'\[\]*><•=()‹?]")
TIME_REGEX = re.compile(r'^((\d{1,2}/\d{1,2}/\d{2,4}|Thursday|Monday|Tuesday|Wednesday|Friday|Saturday|Sunday)|\d{4} ).*')

SUPPRESS_LOGS_FOR_AUTHORS = [
    'Multiple Senders Multiple Senders',
    'Undisclosed recipients:',
    'undisclosed-recipients:',
]

# Unhighlighted / uncategorized emailer regexes
ADDITIONAL_CONTACTS = [
    # Custom regex
    Contact(name='Daphne Wallace', emailer_pattern=r"Da[p ]hne Wallace"),
    Contact(name=INTELLIGENCE_SQUARED, emailer_pattern=r"intelligence\s*squared"),
    Contact(name='Matthew Schafer', emailer_pattern=r"matthew\.?schafer?"),
    Contact(name=MICHAEL_BUCHHOLTZ, emailer_pattern=r"Michael.*Buchholtz"),
    Contact(name=SAMUEL_LEFF, emailer_pattern=r"Sam(uel)?(/Walli)? Leff"),
    Contact(name=THANU_BOONYAWATANA, emailer_pattern=r"Thanu (BOONYAWATANA|Cnx)"),
    # No custom regex
    Contact('Amanda Kirby'),
    Contact('Anne Boyles'),
    Contact('Ariane Dwyer'),
    Contact('Brittany Henderson'),
    Contact('Coursera'),
    Contact('Danny Goldberg'),
    Contact(ED_BOYLE),
    Contact('Francesca Hall'),
    Contact('Jeff Pagliuca'),
    Contact('Kevin Bright'),
    Contact(JOHN_PAGE),
    Contact('Kathleen Ruderman'),
    Contact('Larry Cohen'),
    Contact('Michael Simmons'),
    Contact('middle.east.update@hotmail.com'),
    Contact('Nancy Cain'),
    Contact('Nancy Portland'),
    Contact('Oliver Goodenough'),
    Contact('Peter Green'),
    Contact('Steven Victor MD'),
]

HIGHLIGHTED_CONTACTS = flatten([hn.contacts for hn in HIGHLIGHTED_NAMES if isinstance(hn, HighlightedNames)])
ALL_CONTACTS = HIGHLIGHTED_CONTACTS + ADDITIONAL_CONTACTS
CONTACTS_DICT = {c.name: c for c in ALL_CONTACTS}
EMAILER_ID_REGEXES = {c.name: c.emailer_regex for c in ALL_CONTACTS}

# missing_emailers = [ContactInfo(name=n) for n in EMAILERS if n not in EMAILER_ID_REGEXES]
# print(f"MISSING EMAILERS\n\n{ContactInfo.repr_string(missing_emailers)}")


def cleanup_str(_str: str) -> str:
    return BAD_NAME_CHARS_REGEX.sub('', _str.replace(REDACTED, '')).strip().strip('_').strip()


def extract_emailer_names(emailer_str: str) -> list[Name]:
    """Return a list of people's names found in `emailer_str` (email author or recipients field)."""
    raw_names = emailer_str.split(';')
    emailer_str = cleanup_str(emailer_str)

    if raw_names == [REDACTED] or raw_names == [UNKNOWN]:
        return [None]
    elif len(emailer_str) == 0:
        return []

    names_found: list[Name] = [name for name, regex in EMAILER_ID_REGEXES.items() if regex.search(emailer_str)]

    if len(emailer_str) <= 2 or BAD_EMAILER_REGEX.match(emailer_str) or TIME_REGEX.match(emailer_str):
        if len(names_found) == 0 and emailer_str not in SUPPRESS_LOGS_FOR_AUTHORS:
            logger.warning(f"No emailer found in '{escape_single_quotes(emailer_str)}'")
        else:
            logger.info(f"Extracted {len(names_found)} names from semi-invalid '{emailer_str}': {names_found}...")

        return names_found

    names_found = names_found or [emailer_str]
    return [reverse_first_and_last_names(name) for name in names_found]
