#!/usr/bin/env python
import json
import re

from epstein_files.documents.documents.categories import Uninteresting, is_uninteresting
from epstein_files.util.helpers.file_helper import RESEARCH_DATA_REPO_DIR
from epstein_files.util.helpers.string_helper import clean_phone_number
from epstein_files.util.logging import logger, print_text_block
from epstein_files.documents.emails.emailers import PHONE_NUMBER_NAMES
from scripts.use_pickled import console, epstein_files

# +336 48 51 97 51
BAD_PREFIXES = ['0000', '1111', '4444444']
ENTITIES_JSON_PATH = RESEARCH_DATA_REPO_DIR.joinpath('extracted_entities_filtered.json')
US_PHONE_NUMBER_REGEX = re.compile(r"\+?1?\(?\d{3}\)?[-.\s]*\d{3}[-.\s]*\d{4}")
NON_US_PHONE_NUMBER_REGEX = re.compile(r"\+?\d{2,3}[-.\s]*\d[-.\s]*\d{2}[-.\s]*\d{2}[-.\s]*\d{2}[-.\s]*\d{,4}")
PHONE_NUMBER_REGEX = re.compile(r"\b(?<!(real|eger)>)(" + '|'.join([NON_US_PHONE_NUMBER_REGEX.pattern, US_PHONE_NUMBER_REGEX.pattern]) + r')\b')
print(f"\n\n     PHONE_NUMBER_REGEX:  '{PHONE_NUMBER_REGEX.pattern}'\n")

KNOWN_PHONE_NUMBERS = {
    **PHONE_NUMBER_NAMES,
    '3407151040': 'IRS',
    '8004804111': 'JP Morgan',
    '3407761600': 'Antilles School',
    '3102851307': 'The Beverly Hilton',
    '3104721211': 'Bel Air Hotel in LA',
    '9544678204': 'court reporter',
}

entities_json = json.loads(ENTITIES_JSON_PATH.read_text())
console.print_json(json.dumps({k: e.name for k, e in PHONE_NUMBER_NAMES.items()}))


for doc in epstein_files._documents:
    if is_uninteresting(doc.category):
        doc._warn(f"Skipping category {doc.category}...")
        continue
    elif doc.file_info.is_local_extract_file:
        doc._warn(f"Skipping local extract...")
        continue
    # elif 'phone logs' in doc._config.complete_description

    doc_msgs = {}

    for phone_match in PHONE_NUMBER_REGEX.finditer(doc.raw_text()):
        phone_number = clean_phone_number(phone_match.group(0))

        if any(phone_number.startswith(prefix) for prefix in BAD_PREFIXES) or phone_number in KNOWN_PHONE_NUMBERS:
            continue

        if phone_match.group(0).startswith('+'):
            phone_number = '+' + phone_number

        doc_msgs[phone_number] = f"Found phone number: {phone_number}"

    if doc_msgs:
        console.print(doc._summary_panel, f"found {len(doc_msgs)} phone numbers")

        for number, msg in doc_msgs.items():
            console.print(f'   -> {msg}')

        if 'daily schedule' in doc._config.note:
            doc.print_untruncated()

        console.line()


# for entity in entities_json['phones']:
#     name = entity['entity_value']
#     clean_name = clean_phone_number(name)
#     entity_type = entity['entity_type']
#     doc_ids = entity['efta_numbers']
#     entity_str = f"{clean_name} appears in {len(doc_ids):,} documents"

#     if any(entity_str.startswith(prefix) for prefix in BAD_PREFIXES):
#         logger.info(f"skipping bad number {entity_str}")
#         continue

#     # print_text_block(json.dumps(entity), f"{entity_str}, type '{entity_type}'")
#     print('')
#     logger.warning(entity_str)

#     for id in doc_ids:
#         try:
#             doc = epstein_files.get_id(id)
#             console.print(doc)
#         except KeyError:
#             logger.warning(f"    -> {id} not found for {entity_str}...")
#             continue
