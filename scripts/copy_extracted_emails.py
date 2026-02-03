#!/usr/bin/env python
# Copy any emails extracted from legal filings into the repo.
import shutil

from scripts.use_pickled import console, epstein_files
from epstein_files.util.file_helper import EXTRACTED_EMAILS_DIR


for email in epstein_files.emails:
    if email.is_local_extract_file:
        new_path = EXTRACTED_EMAILS_DIR.joinpath(email.filename)
        console.print(email.summary)
        console.print(f'   Copying to "{new_path}"\n')
        shutil.copy2(email.file_path, new_path)
