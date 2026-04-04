import csv
from pathlib import Path

# from epstein_files.documents.emails.emailers import ENTITIES_DICT
from epstein_files.output.rich import console, print_json
from epstein_files.people.entity import Entity
from epstein_files.util.helpers.data_helpers import listify, without_falsey, uniq_sorted
from epstein_files.util.helpers.string_helper import (as_pattern, clean_phone_number, indented, is_integer,
     join_patterns, join_truthy, join_truthy_args, quote, remove_question_marks)
from epstein_files.util.logging import logger

BLACK_BOOK_CSV_PATH = Path(__file__).parent.joinpath('black-book-lines.txt')
UNUSED_COLS = ['Page', 'Page-Link']

BLACK_BOOK_PHONE_NUMBER_COLS = [
    "Phone (h) – home",
    "Phone (no specifics)",
    "Phone (p) – portable/mobile",
    "Phone (w) – work",
]


def add_black_book_entities(entities: dict[str, Entity]) -> dict[str, Entity]:
    """Read the Black book CSV from https://epsteinsblackbook.com/data/black-book-lines.txt."""
    new_entities = []
    i = 0

    with open(BLACK_BOOK_CSV_PATH, mode ='r') as file:
        for i, row in enumerate(csv.DictReader(file)):
            row_dict = {k: v for k, v in row.items() if k not in UNUSED_COLS}
            new_entity = _from_black_book(row_dict)

            if (existing_entity := entities.get(new_entity.name)):
                old_num_phone_numbers = len(existing_entity.phone_numbers)
                existing_entity.phone_numbers = uniq_sorted(existing_entity.phone_numbers + new_entity.phone_numbers)

                if (num_phone_numbers_added := len(existing_entity.phone_numbers) - old_num_phone_numbers):
                    existing_entity._warn(f'added {num_phone_numbers_added} new phone numbers')
                else:
                    existing_entity._warn(f"no new phone numbers (has {len(existing_entity.phone_numbers)})")
            else:
                new_entities.append(new_entity)
                print_json({k: v for k, v in row_dict.items() if v}, new_entity.name)
                msg = (new_entity.bio_txt.append(f" ({len(new_entity.phone_numbers)} phone numbers: {', '.join(new_entity.phone_numbers)})", 'cyan'))
                new_entity._warn(f'is new from black book {msg}')

    logger.warning(f"Found {i - len(new_entities)} existing Entity objects out of {i} blackbook records\n")
    return entities


def _from_black_book(black_book_row: dict[str, str]) -> Entity:
        """Builed an `Entity` from a CSV row of Epstein's black book."""
        from epstein_files.output.highlight_config import get_highlight_group_for_name
        from epstein_files.output.highlighted_names import HighlightedNames

        full_name = black_book_row['Name']
        first_name = black_book_row['First Name']
        last_name = black_book_row['Surname']
        name = join_truthy_args(first_name, last_name)
        country = black_book_row['Country']
        phone_numbers = []
        category = ''

        if country.lower() in ['us', 'u.s.', 'united states', 'new york']:
            country = ''
        elif (group := get_highlight_group_for_name(country)) and isinstance(group, HighlightedNames):
            category = group.category

        if (first_name and first_name not in full_name) or (last_name and last_name not in full_name):
            if not full_name.startswith('Important'):
                logger.warning(f"Too many names (name='{full_name}', first_name='{first_name}', last_name='{last_name}')")

        if '(' in name:
            logger.error(f"Found '(' in entity name '{name}'")
            name = name.replace('(', '').replace(')', '').strip()

        if '?' in name:
            logger.error(f"Found '?' in entity name '{name}'")
            name = name.replace('?', '').strip()

        for number in without_falsey([v for k, v in black_book_row.items() if k in BLACK_BOOK_PHONE_NUMBER_COLS]):
            numbers = number.split('|') if '|' in number else [number]
            numbers = [n.split('(')[0].strip() for n in numbers]
            phone_numbers.extend(without_falsey(numbers))

        location = join_truthy_args(black_book_row['City'], country)

        return Entity(
            name=name or join_truthy(first_name, last_name),
            info=join_truthy_args(black_book_row["Company/Add. Text"], location),
            category=category,
            email_addresses=without_falsey([black_book_row['Email']]),
            phone_numbers=phone_numbers,
        )
