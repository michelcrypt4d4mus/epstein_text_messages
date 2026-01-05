#!/usr/bin/env python
# Print email ID + timestamp
from collections import defaultdict

from rich.markup import escape
from rich.panel import Panel

from scripts.use_pickled import epstein_files
from epstein_files.util.data import sort_dict
from epstein_files.util.rich import console, print_json


max_sizes = defaultdict(int)
counts = defaultdict(int)

# for doc in sorted(epstein_files.all_documents(), key=lambda e: e.file_id):
#     max_file_sizes[doc.class_name()] = max(max_file_sizes[doc.class_name()], doc.file_size())
#     console.print(doc.summary())
#     print_json('metadata', doc.metadata())

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

for id_count in sort_dict(max_sizes):
    id = id_count[0]
    count = id_count[1]
    email = epstein_files.get_documents_by_id([id])[0]
    console.print(f"{count:6d}: {email.summary().plain}")


console.line(2)
console.print('counts', counts)
