"""
Constants and methods for identifying people in email headers.
"""
import re

from epstein_files.output.highlight_config import HIGHLIGHTED_ENTITIES
from epstein_files.people.entity import Entity, organization
from epstein_files.people.names import *
from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.helpers.data_helpers import escape_single_quotes, flatten, groupby, uniq_sorted
from epstein_files.util.logging import logger

BAD_EMAILER_REGEX = re.compile(r'^(>|11111111)|agreed|ok(?!asha)|sexy|re:|fwd:|LIMITED PARTNERS|Multiple Senders|((sent|attachments|subject|importance).*|.*(january|201\d|hysterical|i have|image0|so that people|article 1.?|PROSPECTIVE INVESTORS|momminnemummin|These conspiracy theories|your state|undisclosed|www\.theguardian|talk in|it was a|what do|cc:|call (back|me)|afiaata|[IM]{4,}).*)$', re.IGNORECASE)
BAD_NAME_CHARS_REGEX = re.compile(r"[\"'\[\]*><•=()‹?]")
TIME_REGEX = re.compile(r'^((\d{1,2}/\d{1,2}/\d{2,4}|Thursday|Monday|Tuesday|Wednesday|Friday|Saturday|Sunday)|\d{4} ).*')

# Unhighlighted / uncategorized emailers we don't know much about but need regexes to identify
ADDITIONAL_CONTACTS = [
    # Custom regex
    Entity('BS Stern', emailer_pattern=r"BS Ste(m|rn)"),
    Entity(INTELLIGENCE_SQUARED, emailer_pattern=r"intelligence\s*squared"),
    Entity('Matthew Schafer', emailer_pattern=r"matthew\.?schafer?"),
    Entity(MICHAEL_BUCHHOLTZ, emailer_pattern=r"Michael.*Buchholtz"),
    Entity(SAMUEL_LEFF, emailer_pattern=r"Sam(uel)?(/Walli)? Leff"),
    Entity(THANU_BOONYAWATANA, emailer_pattern=r"Thanu (BOONYAWATANA|Cnx)"),
    # No custom regex
    Entity('Amanda Kirby'),
    Entity('Anne Boyles', match_partial=None),
    Entity('Ariane Dwyer'),
    Entity('Brittany Henderson'),
    Entity('Danny Goldberg', match_partial=None),
    Entity('Jeff Pagliuca'),
    Entity(JOHN_PAGE, match_partial=None),
    Entity('Julie Shample'),
    Entity('Kathleen Ruderman'),
    Entity('Kevin Bright', match_partial=None),
    Entity('Larry Cohen', match_partial=None),
    Entity('Lawrence Delson'),
    Entity('Martin Zeman'),
    Entity('Michael Simmons', match_partial=None),
    Entity('middle.east.update@hotmail.com'),
    Entity('Nancy Cain'),
    Entity('Nancy Portland', match_partial=None),
    Entity(OLIVER_GOODENOUGH),
    Entity('Peter Green', match_partial=None),
    Entity('Sarah Mapes'),
    Entity('Stewart Oldfield'),
]

SUPPRESS_LOGS_FOR_AUTHORS = [
    'Multiple Senders Multiple Senders',
    'Undisclosed recipients:',
    'undisclosed-recipients:',
]

# Collect all configured entities into various data structures
CONFIGURED_ENTITIES = HIGHLIGHTED_ENTITIES + ADDITIONAL_CONTACTS
EMAILER_REGEXES = {c.name: c.emailer_regex for c in CONFIGURED_ENTITIES if c.is_emailer}
ENTITY_CATEGORIES = groupby(CONFIGURED_ENTITIES, lambda contact: contact.category)
ENTITIES_DICT = {c.name: c for c in CONFIGURED_ENTITIES}
UNCONFIGURED_ENTITIES_ENCOUNTERED = {}
assert len(CONFIGURED_ENTITIES) == len(ENTITIES_DICT), f"{len(CONFIGURED_ENTITIES)} entities but only {len(ENTITIES_DICT)} names!"

# Strings that usually signify an identity if present in email body
IDENTIFYING_STRINGS = {}

for contact in CONFIGURED_ENTITIES:
    for identifier in contact.identifying_strings:
        IDENTIFYING_STRINGS[identifier] = contact

# file IDs that contain a unique signifier but do not involve that person
UNIQ_IDENTIFIER_FALSE_ALARMS = ['EFTA00961792']


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

    names_found: list[Name] = [name for name, regex in EMAILER_REGEXES.items() if regex.search(emailer_str)]

    if len(emailer_str) <= 2 or BAD_EMAILER_REGEX.match(emailer_str) or TIME_REGEX.match(emailer_str):
        if len(names_found) == 0 and emailer_str not in SUPPRESS_LOGS_FOR_AUTHORS:
            logger.warning(f"No emailer found in '{escape_single_quotes(emailer_str)}'")
        else:
            logger.info(f"Extracted {len(names_found)} names from semi-invalid '{emailer_str}': {names_found}...")

        return names_found

    names_found = [reverse_first_and_last_names(name) for name in (names_found or [emailer_str])]
    logger.debug(f"names_found in '{emailer_str}': {names_found}")
    return names_found


def get_entity(name: str | Entity) -> Entity:
    if isinstance(name, Entity):
        return name
    elif name in ENTITIES_DICT:
        return ENTITIES_DICT[name]
    elif name not in UNCONFIGURED_ENTITIES_ENCOUNTERED:
        logger.warning(f"Encountered unconfigured entity name '{name}'")
        UNCONFIGURED_ENTITIES_ENCOUNTERED[name] = Entity(name)

    return UNCONFIGURED_ENTITIES_ENCOUNTERED[name]


def get_entities(_names: Sequence[str | Entity]) -> list[Entity]:
    """Also uniquifies."""
    names = [n.name if isinstance(n, Entity) else n for n in _names]
    return [get_entity(name) for name in uniq_sorted(names)]
