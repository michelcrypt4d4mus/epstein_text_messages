#!/usr/bin/env python
# Print email ID + timestamp
from dotenv import load_dotenv
load_dotenv()

from epstein_files.epstein_files import EpsteinFiles


epstein_files = EpsteinFiles()

for email in sorted(epstein_files.emails, key=lambda e: e.file_id):
    print(f"{email.file_id},{email.timestamp}")
