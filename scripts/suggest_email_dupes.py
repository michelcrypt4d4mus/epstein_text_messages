#!/usr/bin/env python
# Look for emails with exact same timstamp and suggest them for suppression
from dotenv import load_dotenv
load_dotenv()

from epstein_files.documents.document import Document
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.rich import *

OK_FILE_IDS = ['025594', '025603']

email_timestamps = {}


for email in EpsteinFiles.get_files().emails:
    if email.timestamp not in email_timestamps:
        email_timestamps[email.timestamp] = email
        continue

    other_email = email_timestamps[email.timestamp]

    if other_email.url_slug == email.url_slug:
        console.print(f"Skipping same url_slug for '{email.filename}'...", style='dim')
        continue
    elif other_email.is_duplicate or email.is_duplicate:
        console.print(f"Skipping already suppressed '{email.filename}'...", style='dim')
        continue
    elif email.file_id in OK_FILE_IDS:
        console.print(f"Skipping OK_FILE_IDS '{email.filename}'", style='dim')
        continue

    console.print(f"\ncollision between {other_email.file_id} and {email.file_id}")
    console.print(f"    {other_email.filename}: {other_email.description()}")
    console.print(f"    {email.filename}: {email.summary}")
    Document.diff_files([str(email.filename), str(other_email.filename)])
