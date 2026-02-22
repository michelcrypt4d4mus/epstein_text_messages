#!/usr/bin/env python
# Print email ID + timestamp
import logging
import sys
from collections import defaultdict
from datetime import datetime

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.epstein_files import document_cls
from epstein_files.documents.document import Document
from epstein_files.documents.email import Email, UNINTERESTING_EMAILERS
from epstein_files.documents.emails.constants import FALLBACK_TIMESTAMP
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import HIGHLIGHT_GROUPS, get_style_for_name
from epstein_files.output.highlighted_names import HighlightedNames
from epstein_files.util.constant.names import *
from epstein_files.util.constants import CONFIGS_BY_ID, EmailCfg
from epstein_files.util.helpers.data_helpers import *
from epstein_files.util.helpers.debugging_helper import print_all_timestamps, print_file_counts
from epstein_files.util.helpers.string_helper import quote
from epstein_files.util.logging import logger
from epstein_files.output.rich import bool_txt, console, highlighter, styled_key_value, print_subtitle_panel

DILORIO_SPLIT = '\nFrom: Chris'


dilorio = epstein_files.person_objs([CHRISTOPHER_DILORIO])[0]
uniquify([e.timestamp for e in dilorio.emails])
sub_emails = []
skipped = []

for big_email in dilorio.emails:
    big_email = big_email.reload()

    texts = [
        (f"{DILORIO_SPLIT}{t}" if i > 0 else t).strip()
        for i, t in enumerate(big_email.text.split(DILORIO_SPLIT))
    ]

    if len(texts) == 1:
        logger.warning(f"No sub emails to create...")
        import pdb;pdb.set_trace()
        continue
    else:
        logger.warning(f"Parsing {big_email} into {len(texts)} sub emails...")
        big_email._was_split_up = True

    for i, text in enumerate(texts, 1):
        console.line()
        print_subtitle_panel(f"Sub email #{i} ({len(text)} chars) Raw")
        console.print(text)
        new_file_stem = big_email.file_info.file_stem + f'_{i}.txt'
        email = Email(big_email.file_path.parent.joinpath(new_file_stem), text=text)
        email.extracted_author = CHRISTOPHER_DILORIO
        print_subtitle_panel(f"Email object for #{new_file_stem} ({len(text)} chars)")
        console.print(email)

        if not email.actual_text or email.lines[-1].startswith('Subject:'):
            print(f"length of actual_text: {email.actual_text}\n{email.actual_text}")
            email.warn(f"skipping empty email...")
            import pdb;pdb.set_trace()
            continue

        sub_emails.append(email)

        if email.timestamp > datetime(2026, 1, 1):
            email.warn(f"Bad timestamp: {email.timestamp}")
            big_email.file_info.open()
            big_email.file_info.open_pdf()
            import pdb;pdb.set_trace()

unique_timestamps = uniquify([e.timestamp for e in sub_emails])
logger.warning(f"Created {len(sub_emails)} sub emails with {len(unique_timestamps)} unique timestamps from {len(dilorio.emails)} {CHRISTOPHER_DILORIO} emails")

for email in sub_emails:
    if email.timestamp > datetime(2026, 1, 1):
        email.warn(f"Bad timestamp: {email.timestamp}")
