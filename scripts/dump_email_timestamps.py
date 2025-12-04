#!/usr/bin/env python
# Print email ID + timestamp
from dotenv import load_dotenv
load_dotenv()
from rich.text import Text

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.constant.names import JEFFREY_EPSTEIN
from epstein_files.util.rich import console


epstein_files = EpsteinFiles.get_files()

# for email in sorted(epstein_files.emails, key=lambda e: e.file_id):
#     print(f"{email.file_id},{email.timestamp}")
#     # console.print(Text(email.file_id + ": ").append(str(email.recipients)))


epstein_emails = [e for e in epstein_files.emails if e.author == JEFFREY_EPSTEIN]

for email in sorted(epstein_emails, key=lambda e: -len(e.actual_text)):
    console.print(email.description())
    console.print(email.actual_text)
    console.line(2)
