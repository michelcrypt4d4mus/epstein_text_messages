#!/usr/bin/env python
# Print email ID + timestamp
from dotenv import load_dotenv
load_dotenv()
from rich.panel import Panel
from rich.text import Text

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.constant.names import JEFFREY_EPSTEIN
from epstein_files.util.rich import console


epstein_files = EpsteinFiles.get_files()

# for email in sorted(epstein_files.emails, key=lambda e: e.file_id):
#     print(f"{email.file_id},{email.timestamp}")
#     # console.print(Text(email.file_id + ": ").append(str(email.recipients)))


epstein_emails = [e for e in epstein_files.emails if e.author == JEFFREY_EPSTEIN]

#for email in sorted(epstein_files.emails, key=lambda e: -len(e.actual_text)):
for email in sorted(epstein_files.emails, key=lambda e: e.timestamp):
    if email.is_junk_mail:
        continue

    console.print(email.description())
    console.print(Panel(email.actual_text[0:700], title='actual_text'))
    console.print(Panel(email.text[0:400], title='raw_text'), style='wheat4')
    console.line(2)
