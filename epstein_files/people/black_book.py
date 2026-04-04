import csv
from pathlib import Path

from epstein_files.documents.emails.emailers import ENTITIES_DICT
from epstein_files.output.rich import console, print_json
from epstein_files.people.entity import Entity
from epstein_files.util.helpers.string_helper import clean_phone_number

BLACK_BOOK_CSV_PATH = Path(__file__).parent.joinpath('black-book-lines.txt')
UNUSED_COLS = ['Page', 'Page-Link']


def get_black_book() -> list[Entity]:
    """Read the Black book CSV from https://epsteinsblackbook.com/data/black-book-lines.txt."""
    entities = []

    with open(BLACK_BOOK_CSV_PATH, mode ='r') as file:
        for row in csv.DictReader(file):
            row_dict = {k: v for k, v in row.items() if k not in UNUSED_COLS}
            entity = Entity.from_black_book(row_dict)

            if entity.name in ENTITIES_DICT:
                entity._warn('already exists in ENTITIES_DICT, check phone numbers')
            else:
                entity._warn('new from black book')
                print_json({k: v for k, v in row_dict.items() if v}, entity.name)
                console.print(entity.bio_txt.append(f" with {len(entity.phone_numbers)} phone numbers ({', '.join(entity.phone_numbers)})", 'cyan'))

    return entities
