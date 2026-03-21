#!/usr/bin/env python
# Print email ID + timestamp
import logging
import sys
from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.epstein_files import document_cls
from epstein_files.documents.document import Document
from epstein_files.documents.email import Email, UNINTERESTING_EMAILERS
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import HIGHLIGHT_GROUPS, get_style_for_name
from epstein_files.output.highlighted_names import HighlightedNames
from epstein_files.output.html.builder import table_to_html, write_templated_html
from epstein_files.people.person import Person
from epstein_files.people.names import *
from epstein_files.util.constants import CONFIGS_BY_ID, EmailCfg, UNINTERESTING_OTHER_FILE_IDS
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import *
from epstein_files.util.helpers.debugging_helper import print_all_timestamps, print_file_counts
from epstein_files.util.helpers.file_helper import open_file_or_url
from epstein_files.util.helpers.string_helper import extract_emojis, quote
from epstein_files.util.logging import logger, print_text_block
from epstein_files.output.rich import bool_txt, console, highlighter, print_subtitle_panel


num_missing_unknown_recipient = 0
num_interesting = 0
num_uninteresting = 0
num_word_count_worthy = 0
ids = UNINTERESTING_OTHER_FILE_IDS

for doc in epstein_files.unique_documents:
    if doc._config.truncate_to == 'auto':
        console.print(f"{doc.file_id} has truncate_to set to {doc._config.truncate_to}", doc._summary, '\n')
        console.print(doc)
        console.line(2)

sys.exit()



def print_first_emails():
    emailers = sorted(epstein_files.emailers, key=lambda e: e.earliest_email_at)

    for emailer in emailers:
        first_email = emailer.emails[0]

        if emailer.is_interesting or first_email.is_fwded_article:
            continue
        elif first_email._truncate_to_length() >= first_email.length:
            logger.warning(f"User '{emailer.name}' first email is untruncated")
            continue
        elif emailer.should_always_truncate:
            logger.warning(f"Skipping truncatable user '{emailer.name}'")
            continue

        print_subtitle_panel(emailer.name_str)
        console.print(emailer.emails[0])

print_first_emails()
sys.exit()


print_partial_names_used_in_regexes()
max_sizes = defaultdict(int)
counts = defaultdict(int)

# for doc in sorted(epstein_files.documents, key=lambda e: e.file_id):
#     max_file_sizes[doc.class_name()] = max(max_file_sizes[doc.class_name()], doc.file_size())
#     console.print(doc.summary)
#     print_json('metadata', doc.metadata())


def print_potential_uninteresting_emailers():
    emailers = sorted(epstein_files.emailers, key=lambda e: epstein_files.earliest_email_at(e.name))

    for emailer in emailers:
        emails = emailer.emails
        emails_sent_by = [e for e in emails if e.author == emailer]
        emailer_str = f"(useless emailer) {emailer}" if emailer in UNINTERESTING_EMAILERS else emailer
        txt = Text('')

        if len(emails) == 1:
            if len(emails_sent_by) == 1:
                console.print(txt.append('     [SENT ONE]', style='bright_green dim').append(highlighter(f" {emailer_str} ({len(emails[0].recipients)} recipients)")))
            else:
                console.print(txt.append(' [RECEIVED ONE]', style='bright_red dim').append(highlighter(f" {emailer_str} ({len(emails[0].recipients)} recipients)")))
        elif len(emails_sent_by) == 0:
            console.print(txt.append('    [NONE SENT]', style='dim').append(highlighter(f" {emailer_str} received {len(emails)} emails but sent none")))
        elif get_style_for_name(emailer.name, default_style='none') == 'none':
            console.print(Text('     [NO STYLE]', style='wheat4').append(highlighter(f" {emailer_str} has no associated styling")))


print_potential_uninteresting_emailers()
sys.exit()
counts = defaultdict(int)


for email in sorted(epstein_files.emails, key=lambda e: -len(e.actual_text)):
    if email.is_fwded_article or email.is_mailing_list or email.is_duplicate:
        if email.is_fwded_article:
            counts['fwd'] += 1
        elif email.is_mailing_list:
            counts['mailing_list'] += 1
        elif email.is_duplicate:
            counts['dupe'] += 1

        continue

    if len(email.actual_text) > 100:
        max_sizes[email.file_id] = len(email.actual_text)
        console.line(2)
        console.print(Panel(email._summary, expand=False, style=email.border_style))
        console.print(escape(email._extract_actual_text()))

console.line(2)

for i, id_count in enumerate(sort_dict(max_sizes)):
    if i > 50:
        continue

    id = id_count[0]
    count = id_count[1]
    email = epstein_files.get_ids([id])[0]
    console.print(f"{count:6d}: {email._summary.plain}")


console.line(2)
console.print('counts', counts)
