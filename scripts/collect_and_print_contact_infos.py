#!/usr/bin/env python
# Print emailer regex and person bio info as repr() strings
import logging
import sys
from collections import defaultdict

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.emails.emailers import EMAILER_ID_REGEXES
from epstein_files.people.contact_info import Contact
from epstein_files.util.constant.names import *
from epstein_files.util.helpers.data_helpers import *
from epstein_files.util.helpers.file_helper import log_file_write
from epstein_files.util.helpers.string_helper import indented
from epstein_files.output.highlight_config import HIGHLIGHTED_NAMES, get_style_for_name
from epstein_files.output.highlighted_names import HighlightedNames
from epstein_files.util.logging import logger
from epstein_files.util.rich import console, highlighter, print_json, print_subtitle_panel

CONTACT_INFOS_PY_PATH = 'epstein_files/people/contact_infos.py'
VAR_NAME = 'CONTACT_INFOS'
BASE_INDENT = 8


def repr_string(contact_infos: list[Contact]) -> str:
    return '[\n' + indented(',\n'.join([repr(contact) for contact in contact_infos]), 4) + '\n],'


contact_infos = {}
unhighlighted_contact_infos = {}

for cfg in HIGHLIGHTED_NAMES:
    if not isinstance(cfg, HighlightedNames):
        continue
    elif not cfg.emailers:
        continue

    cfg_contact_infos = {
        name: Contact(
            name=name,
            emailer_pattern=EMAILER_ID_PATTERNS.get(name) or '',
            info=info or ''
        )
        for name, info in cfg.emailers.items()
    }

    contact_infos.update(cfg_contact_infos)
    cfg_contacts = [ci for ci in cfg_contact_infos.values()]
    contacts_str = indented(f"contacts={repr_string(cfg_contacts)}", BASE_INDENT)
    print_subtitle_panel(cfg.label)
    print(contacts_str)

# Append any missing regex patterns
for name, pattern in EMAILER_ID_PATTERNS.items():
    if name not in contact_infos:
        logger.warning(f"Appending regex for '{name}': '{pattern}'")
        contact_infos[name] = Contact(name=name, emailer_pattern=pattern)
        unhighlighted_contact_infos[name] = contact_infos[name]

vars_string = ',\n'.join([repr(contact) for contact in unhighlighted_contact_infos.values()])
python_str = f"from epstein_files.util.constant.names import *\n\n\n# Unhighlighted / uncategorized emailer regexes\n"
python_str += f'{VAR_NAME} = [\n' + indented(vars_string) + '\n]\n\n'
python_str += f"{VAR_NAME}_DICT = {{contact.name: contact for contact in {VAR_NAME}}}\n\n"
print(python_str)

with open(CONTACT_INFOS_PY_PATH, 'wt') as f:
    f.write(f"from epstein_files.util.constant.names import *\n\n\n")
    f.write(python_str)
    log_file_write(CONTACT_INFOS_PY_PATH)
