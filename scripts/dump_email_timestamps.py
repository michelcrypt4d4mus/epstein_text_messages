#!/usr/bin/env python
# Print email ID + timestamp
import logging
import sys
from collections import defaultdict

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.documents.document import Document
from epstein_files.documents.email import UNINTERESTING_EMAILERS
from epstein_files.util.constant.names import *
from epstein_files.util.constants import ALL_FILE_CONFIGS
from epstein_files.util.data import *
from epstein_files.util.highlighted_group import HIGHLIGHTED_NAMES, HighlightedNames, get_style_for_name
from epstein_files.util.logging import logger
from epstein_files.util.rich import console, highlighter, print_json


def print_partial_names_used_in_regexes():
    names = []
    partial_name_counts = defaultdict(int)

    for highlight in HIGHLIGHTED_NAMES:
        if type(highlight) != HighlightedNames:
            continue
        elif not highlight.should_match_first_last_name:
            continue

        for name in highlight.emailers:
            for partial_name in [n.lower() for n in [extract_first_name(name), extract_last_name(name)]]:
                partial_name_counts[partial_name] += 1

                if partial_name not in NAMES_TO_NOT_HIGHLIGHT:
                    names.append(partial_name)
                    print(f"name='{name}', partial_name='{partial_name}'")

    print('\n'.join(sorted(names)))
    print(f"\n\n")

    for name, count in partial_name_counts.items():
        if count > 1:
            print(f"partial name '{name}' appears {count} times")

    sys.exit()


print_partial_names_used_in_regexes()
max_sizes = defaultdict(int)
counts = defaultdict(int)

# for doc in sorted(epstein_files.all_documents(), key=lambda e: e.file_id):
#     max_file_sizes[doc.class_name()] = max(max_file_sizes[doc.class_name()], doc.file_size())
#     console.print(doc.summary())
#     print_json('metadata', doc.metadata())


def print_potential_uninteresting_emailers():
    emailers = sorted(epstein_files.emailers(), key=lambda e: epstein_files.earliest_email_at(e))

    for emailer in emailers:
        emails = epstein_files.emails_for(emailer)
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
        elif get_style_for_name(emailer, default_style='none') == 'none':
            console.print(Text('     [NO STYLE]', style='wheat4').append(highlighter(f" {emailer_str} has no associated styling")))


print_potential_uninteresting_emailers()
sys.exit()
counts = defaultdict(int)


for email in sorted(epstein_files.emails, key=lambda e: -len(e.actual_text)):
    if email.is_fwded_article() or email.is_mailing_list() or email.is_duplicate():
        if email.is_fwded_article():
            counts['fwd'] += 1
        elif email.is_mailing_list():
            counts['mailing_list'] += 1
        elif email.is_duplicate():
            counts['dupe'] += 1

        continue

    if len(email.actual_text) > 100:
        max_sizes[email.file_id] = len(email.actual_text)
        console.line(2)
        console.print(Panel(email.summary(), expand=False, style=email._border_style()))
        console.print(escape(email._actual_text()))

console.line(2)

for i, id_count in enumerate(sort_dict(max_sizes)):
    if i > 50:
        continue

    id = id_count[0]
    count = id_count[1]
    email = epstein_files.for_ids([id])[0]
    console.print(f"{count:6d}: {email.summary().plain}")


console.line(2)
console.print('counts', counts)
