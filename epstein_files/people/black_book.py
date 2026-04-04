import csv
import re
from pathlib import Path

import phonenumbers

# from epstein_files.documents.emails.emailers import ENTITIES_DICT
from epstein_files.output.rich import console, print_json
from epstein_files.people.entity import Entity
from epstein_files.util.helpers.data_helpers import listify, without_falsey, uniq_sorted
from epstein_files.util.helpers.string_helper import (as_pattern, clean_phone_number, indented, is_integer,
     join_patterns, join_truthy, join_truthy_args, quote, remove_question_marks)
from epstein_files.util.logging import logger
from epstein_files.util.timer import Timer

BLACK_BOOK_CSV_PATH = Path(__file__).parent.joinpath('black-book-lines.txt')
UNUSED_COLS = ['Page', 'Page-Link']
STRIP_NOTES_REGEX = re.compile(r"(.{7}[^(]+)(\s*\(.+\))?")  # match non parens after 7 chars to avoid (212) etc

BLACK_BOOK_PHONE_NUMBER_COLS = [
    "Phone (h) – home",
    "Phone (no specifics)",
    "Phone (p) – portable/mobile",
    "Phone (w) – work",
]


def add_black_book_entities(entities: dict[str, Entity]) -> dict[str, Entity]:
    """Read the Black book CSV from https://epsteinsblackbook.com/data/black-book-lines.txt."""
    from epstein_files.output.highlight_config import get_entity
    timer = Timer()
    new_entities = []
    i = 0

    with open(BLACK_BOOK_CSV_PATH, mode ='r') as file:
        for i, row in enumerate(csv.DictReader(file)):
            row_dict = {k: v for k, v in row.items() if k not in UNUSED_COLS}
            new_entity = _from_black_book(row_dict)
            # print_json({k: v for k, v in row_dict.items() if v}, new_entity.name)

            if (existing_entity := entities.get(new_entity.name, get_entity(new_entity.name))):
                old_num_phone_numbers = len(existing_entity.phone_numbers)
                existing_entity.phone_numbers = uniq_sorted(existing_entity.phone_numbers + new_entity.phone_numbers)

                if (num_phone_numbers_added := len(existing_entity.phone_numbers) - old_num_phone_numbers):
                    existing_entity._debug_log(f'added {num_phone_numbers_added} new phone numbers')
                else:
                    existing_entity._debug_log(f"no new phone numbers (has {len(existing_entity.phone_numbers)})")
            else:
                new_entities.append(new_entity)
                entities[new_entity.name] = new_entity
                msg = (new_entity.bio_txt.append(f" ({len(new_entity.phone_numbers)} phone numbers: {', '.join(new_entity.phone_numbers)})", 'cyan'))
                new_entity._warn(f'is new from black book {msg}')

    timer.print_at_checkpoint(f"Added {len(new_entities)} new Entities, updated {i - len(new_entities)} existing from{i} blackbook records")
    # logger.warning(f"Added {len(new_entities)} new Entities, updated {i - len(new_entities)} existing from{i} blackbook records\n")
    return entities


def _from_black_book(black_book_row: dict[str, str]) -> Entity:
    """Builed an `Entity` from a CSV row of Epstein's black book."""
    from epstein_files.output.highlight_config import get_entity, get_highlight_group_for_name
    from epstein_files.output.highlighted_names import HighlightedNames

    full_name = black_book_row['Name']
    first_name = black_book_row['First Name']
    last_name = black_book_row['Surname'] or (full_name if first_name not in full_name else '')
    name = join_truthy_args(first_name, last_name) or full_name
    info_suffix = ''
    phone_numbers = []
    category = ''

    if (country := black_book_row['Country']).lower() in ['us', 'u.s.', 'united states', 'new york']:
        country = ''
    elif (group := get_highlight_group_for_name(country)) and isinstance(group, HighlightedNames):
        category = group.category

    if '(' in name or '?' in name:
        logger.debug(f"Found '(' or '?' in entity name '{name}'")
        name = name.replace('(', '').replace(')', '').replace('?', '').strip()

    try:
        reversed_name_pattern = fr"{last_name},? {first_name}"
        reversed_name_regex = re.compile(reversed_name_pattern)
    except Exception as e:
        logger.error(f"failed to compile {reversed_name_pattern}")
        reversed_name_regex = re.compile('.*')

    if not reversed_name_regex.match(full_name) and (full_name not in name or last_name not in full_name):
        if not full_name.startswith('Important'):
            logger.warning(f"Too many names (using '{name}' but Name: '{full_name}')")
            info_suffix = f" ({full_name})"

    for number in without_falsey([v for k, v in black_book_row.items() if k in BLACK_BOOK_PHONE_NUMBER_COLS]):
        # phone numbers are stored as pipe delimited arrays sometimes
        for sub_number in (number.split('|') if '|' in number else [number]):
            sub_number = STRIP_NOTES_REGEX.sub(r"\1", sub_number).replace(' ', '') #()

            if len('0012123969012') == len(sub_number) and sub_number.startswith('001'):
                sub_number = sub_number.removeprefix('001')

            try:
                sub_phone_num = phonenumbers.parse(sub_number, region='US') #, keep_raw_input=True)
                sub_number_fmtted = phonenumbers.format_number(sub_phone_num, phonenumbers.PhoneNumberFormat.NATIONAL) # (sub_phone_num, 'US')
                logger.debug(f"'{sub_number}' has phone #: {sub_number_fmtted}")
                phone_numbers.append(sub_number_fmtted)
            except phonenumbers.phonenumberutil.NumberParseException as e:
                logger.warning(f"failed to create phone number from string '{sub_number}': {e}")
                phone_numbers.append(sub_number)

    location = join_truthy_args(black_book_row['City'], country)

    return Entity(
        name=name,
        info=join_truthy_args(black_book_row["Company/Add. Text"], location) + info_suffix,
        category=category,
        email_addresses=without_falsey([black_book_row['Email']]),
        match_partial=None,
        phone_numbers=phone_numbers,
    )
