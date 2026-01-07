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
from epstein_files.documents.email import USELESS_EMAILERS
from epstein_files.util.constants import ALL_FILE_CONFIGS
from epstein_files.util.data import sort_dict
from epstein_files.util.logging import logger
from epstein_files.util.rich import console, highlighter, print_json


max_sizes = defaultdict(int)
counts = defaultdict(int)

# for doc in sorted(epstein_files.all_documents(), key=lambda e: e.file_id):
#     max_file_sizes[doc.class_name()] = max(max_file_sizes[doc.class_name()], doc.file_size())
#     console.print(doc.summary())
#     print_json('metadata', doc.metadata())

for log in epstein_files.imessage_logs:
    for i, message in enumerate(log.messages):
        try:
            message.parse_timestamp()
        except Exception as e:
            logger.error(f"line {i}, {message}:  {e}")


sys.exit()

def print_potential_useless_emailers():
    emailers = sorted(epstein_files.all_emailers(), key=lambda e: epstein_files.earliest_email_at(e))

    for emailer in emailers:
        emails = epstein_files.emails_for(emailer)
        emails_sent_by = [e for e in emails if e.author == emailer]
        emailer_str = f"(useless emailer) {emailer}" if emailer in USELESS_EMAILERS else emailer

        if len(emails) == 1:
            if len(emails_sent_by) == 1:
                console.print(f"SENT one email: {emailer_str} ({len(emails[0].recipients)} recipients)")
            else:
                console.print(f"RECEIVED only one email: {emailer_str} ({len(emails[0].recipients)} recipients)")
        elif len(emails_sent_by) == 0:
            console.print(f"{emailer_str} received {len(emails)} emails but sent none.")



counts = defaultdict(int)


for email in sorted(epstein_files.emails, key=lambda e: -len(e.actual_text)):
    if email.is_fwded_article() or email.is_junk_mail() or email.is_duplicate():
        if email.is_fwded_article():
            counts['fwd'] += 1
        elif email.is_junk_mail():
            counts['junk'] += 1
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
    email = epstein_files.get_documents_by_id([id])[0]
    console.print(f"{count:6d}: {email.summary().plain}")


console.line(2)
console.print('counts', counts)
