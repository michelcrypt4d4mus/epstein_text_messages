"""
Constants and methods for identifying people in email headers.
"""
import re
from collections import Counter
from typing import Optional

from epstein_files.documents.documents.categories import is_uninteresting
from epstein_files.documents.emails.constants import UNINTERESTING_EMAILERS
from epstein_files.output.highlight_config import HIGHLIGHTED_ENTITIES
from epstein_files.people.entity import COMPANY_SUFFIX_REGEX, Entity, Organization
from epstein_files.people.names import *
from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.helpers.data_helpers import escape_single_quotes, flatten, groupby, uniq_sorted, without_falsey
from epstein_files.util.helpers.string_helper import as_pattern
from epstein_files.util.logging import logger

BAD_EMAILER_REGEX = re.compile(r'^(>|11111111)|agreed|ok(?!asha)|sexy|re:|fwd:|LIMITED PARTNERS|Multiple Senders|((sent|attachments|subject|importance).*|.*(january|201\d|hysterical|i have|image0|so that people|article 1.?|PROSPECTIVE INVESTORS|momminnemummin|These conspiracy theories|your state|undisclosed|www\.theguardian|talk in|it was a|what do|cc:|call (back|me)|afiaata|[IM]{4,}).*)$', re.IGNORECASE)
BAD_NAME_CHARS_REGEX = re.compile(r"[\"'\[\]*><•=()‹?]")
TIME_REGEX = re.compile(r'^((\d{1,2}/\d{1,2}/\d{2,4}|Thursday|Monday|Tuesday|Wednesday|Friday|Saturday|Sunday)|\d{4} ).*')

# Unhighlighted / uncategorized emailers we don't know much about but need regexes to identify
ADDITIONAL_EMAILERS = [
    # Custom regex
    Entity('BS Stern', emailer_pattern=r"BS Ste(m|rn)"),
    Entity(INTELLIGENCE_SQUARED, emailer_pattern=r"intelligence\s*squared"),
    Entity('Matthew Schafer', emailer_pattern=r"matthew\.?schafer?"),
    Entity(SAMUEL_LEFF, emailer_pattern=r"Sam(uel)?(/Walli)? Leff"),
    Entity(THANU_BOONYAWATANA, emailer_pattern=r"Thanu (BOONYAWATANA|Cnx)"),
    # No custom regex
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
    Entity('Michael Simmons', match_partial=None),
    Entity('middle.east.update@hotmail.com'),
    Entity('Nancy Cain'),
    Entity('Nancy Portland', match_partial=None),
    Entity(OLIVER_GOODENOUGH),
    Entity('Peter Green', match_partial=None),
    Entity('Sarah Mapes'),
    # Krassner CCs
    Entity('Barb Cowles', match_partial=None, is_interesting=False),
    Entity('Bob Fass', match_partial=None, is_interesting=False),
    Entity('Caryl Ratner', match_partial=None, is_interesting=False),
    Entity('Daniel Dawson', match_partial=None, is_interesting=False),
    Entity('Holly Krassner Dawson', match_partial=None, is_interesting=False),
    Entity('Lee Quarnstrom', match_partial=None, is_interesting=False),
    Entity('Linda W. Grossman', match_partial=None, is_interesting=False),
    Entity('Lynnie Tofte Fass', match_partial=None, is_interesting=False),
    Entity('Marie Moneysmith', match_partial=None, is_interesting=False),
    Entity('Tom', match_partial=None, is_interesting=False, is_emailer=False),
    Entity('Harry Shearer', match_partial=None, is_interesting=False),
    Entity('Jay Levin', match_partial=None, is_interesting=False),
    Entity('Lanny Swerdlow', match_partial=None, is_interesting=False),
    Entity('Larry Sloman', match_partial=None, is_interesting=False),
    Entity('W&K', match_partial=None, is_interesting=False),
    Entity('Walli Leff', match_partial=None, is_interesting=False),
    Entity('Mrisman02', match_partial=None, is_interesting=False),
    Entity('Nick Kazan', match_partial=None, is_interesting=False),
    Entity('Rebecca Risman', match_partial=None, is_interesting=False),
]

SUPPRESS_LOGS_FOR_AUTHORS = [
    'Multiple Senders Multiple Senders',
    'Undisclosed recipients:',
    'undisclosed-recipients:',
]

# Collect all configured entities into various data structures
CONFIGURED_ENTITIES = HIGHLIGHTED_ENTITIES + ADDITIONAL_EMAILERS
ENTITIES_DICT = {c.name: c for c in CONFIGURED_ENTITIES}

for name in UNINTERESTING_EMAILERS:
    if (entity := ENTITIES_DICT.get(name)):
        entity._debug_log(f"Found UNINTERESTING_EMAILER, setting is_interesting=False...")  # TODO: doesn't mean much right now
        entity.is_interesting = False
    else:
        CONFIGURED_ENTITIES.append(Entity(name, is_interesting=False, match_partial=None))
        CONFIGURED_ENTITIES[-1]._debug_log(f"Created new Entity for UNINTERESTING_EMAILER entry...")

ENTITIES_DICT = {c.name: c for c in CONFIGURED_ENTITIES}  # Rebuild with any new uninteresting mailers
EMAILER_REGEXES = {c.name: c.emailer_regex for c in CONFIGURED_ENTITIES if c.is_emailer}
ENTITY_CATEGORIES = groupby(CONFIGURED_ENTITIES, lambda entity: entity.category)

# TODO: dict of names that are configured but have no Entity. This is filled in in epstein_files.py which sucks.
CONFIGURED_NON_ENTITIES: dict[str, Entity] = {}
UNCONFIGURED_ENTITIES_ENCOUNTERED: dict[str, Entity] = {}

if len(CONFIGURED_ENTITIES) != len(ENTITIES_DICT):
    counts = Counter([c.name for c in CONFIGURED_ENTITIES])
    more_than_one = [k for k, v in counts.items() if v > 1]
    raise ValueError(f"{len(CONFIGURED_ENTITIES)} entities but only {len(ENTITIES_DICT)} names! Bad names: {more_than_one}")


# Strings that usually signify an identity if present in email body
IDENTIFYING_REGEXES = {}

for entity in CONFIGURED_ENTITIES:
    for identifier in entity.identifying_strings:
        IDENTIFYING_REGEXES[re.compile(as_pattern(identifier), re.IGNORECASE)] = entity

# file IDs that contain a unique signifier but do not involve that person
IDENTIFIER_FALSE_ALARMS = ['EFTA00961792']

# Elements of this list will not trigger warnings in get_entity when they are found missing
NO_WARNING_NAMES = [
    '',
    'American Express Travel',
    # 'Leo',
    'Unik',
    'Vlad',
    'karen',
    UNKNOWN,
]


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
    elif emailer_str.lower() in ['j', 'jeff', 'jeffrey']:
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
    elif len(emailer_str) <= 4 and emailer_str.startswith('MM'):
        logger.warning(f"No emailer found in '{escape_single_quotes(emailer_str)}'")
        return []

    names_found = [_reverse_first_and_last_names(name) for name in (names_found or [emailer_str])]
    logger.debug(f"names_found in '{emailer_str}': {names_found}")
    return names_found


def get_entity(name: str | Entity, doc: Optional['Document'] = None) -> Entity:
    if isinstance(name, Entity):
        return name
    elif name in ENTITIES_DICT:
        return ENTITIES_DICT[name]
    elif name in CONFIGURED_NON_ENTITIES:
        return CONFIGURED_NON_ENTITIES[name]  # Avoids spurious warnings
    elif name not in UNCONFIGURED_ENTITIES_ENCOUNTERED:
        if name not in NO_WARNING_NAMES and '@' not in name:
            log = doc._warn if doc else logger.warning
            log(f"Encountered unconfigured entity name '{name}'")

        UNCONFIGURED_ENTITIES_ENCOUNTERED[name] = Entity(name)

    return UNCONFIGURED_ENTITIES_ENCOUNTERED[name]


def get_entities(_names: Sequence[Name | Entity], doc: Optional['Document'] = None) -> list[Entity]:
    """Also uniquifies and removes None / empty string."""
    names = Entity.coerce_entity_names(without_falsey(_names))
    return [get_entity(name, doc) for name in uniq_sorted(names)]


def _reverse_first_and_last_names(name: Name) -> Name:
    """If there's a comma in the name in the style 'Lastname, Firstname', reverse it and remove comma."""
    if name is None:
        return None
    elif '@' in name:
        return name.lower()
    elif COMPANY_SUFFIX_REGEX.match(name):
        return name
    elif ', ' in name:
        names = name.split(', ')
        return f"{names[1]} {names[0]}"
    else:
        return name.removesuffix(' I')  # redaction cruft
