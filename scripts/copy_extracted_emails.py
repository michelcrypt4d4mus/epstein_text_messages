#!/usr/bin/env python
# Copy any emails extracted from legal filings into the repo.
import shutil

from dotenv import load_dotenv
load_dotenv()

from scripts.use_pickled import epstein_files
from epstein_files.util.file_helper import EXTRACTED_EMAILS_DIR
from epstein_files.util.rich import console


for email in epstein_files.emails:
    if email.is_local_extract_file():
        new_path = EXTRACTED_EMAILS_DIR.joinpath(email.filename)
        console.print(email.summary())
        console.print(f'   Copying to "{new_path}"\n')
        shutil.copy2(email.file_path, new_path)
