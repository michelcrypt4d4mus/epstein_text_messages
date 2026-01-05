#!/usr/bin/env python
# Print email ID + timestamp
from collections import defaultdict

from rich.markup import escape
from rich.panel import Panel

from scripts.use_pickled import epstein_files
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.data import iso_timestamp, listify, sort_dict
from epstein_files.util.rich import console, print_json


max_sizes = defaultdict(int)

# for doc in sorted(epstein_files.all_documents(), key=lambda e: e.file_id):
#     max_file_sizes[doc.class_name()] = max(max_file_sizes[doc.class_name()], doc.file_size())
#     console.print(doc.summary())
#     print_json('metadata', doc.metadata())

for email in sorted(epstein_files.emails, key=lambda e: -len(e.actual_text)):
    if email.is_fwded_article() or email.is_junk_mail():
        continue

    if len(email.actual_text) > 100:
        max_sizes[email.file_id] = len(email.actual_text)

    console.print(email.summary())
    console.print(Panel(f"*** {email.filename} actual_text ***", expand=False, style=email._border_style()))
    console.print(escape(email._actual_text()))

console.line(2)
print_json(f"Largest actual_text found", sort_dict(max_sizes))
