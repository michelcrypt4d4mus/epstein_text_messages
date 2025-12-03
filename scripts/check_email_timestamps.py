#!/usr/bin/env python
# Look for emails with exact same timstamp and suggest them for suppression
from dotenv import load_dotenv
load_dotenv()
from rich.console import Console

from epstein_files.documents.document import Document
from epstein_files.documents.email import SUPPRESS_OUTPUT_FOR_EMAIL_IDS
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.rich import *

console = Console(color_system='256')
epstein_files = EpsteinFiles()
email_timestamps = {}


for email in epstein_files.emails:
    if email.timestamp not in email_timestamps:
        email_timestamps[email.timestamp] = email
        continue

    other_email = email_timestamps[email.timestamp]

    if other_email.url_slug == email.url_slug:
        console.print(f"Skipping same url_slug for '{email.filename}'...", style='dim')
        continue
    elif other_email.file_id in SUPPRESS_OUTPUT_FOR_EMAIL_IDS or email.file_id in SUPPRESS_OUTPUT_FOR_EMAIL_IDS:
        console.print(f"Skipping already suppressed '{email.filename}'...", style='dim')
        continue

    console.print(f"\ncollision between {other_email.file_id} and {email.file_id}")
    console.print(f"    {other_email.filename}: {other_email.description()}")
    console.print(f"    {email.filename}: {email.description()}")
    Document.diff_files([str(email.filename), str(other_email.filename)])
