#!/usr/bin/env python
# Search the document text AFTER all OCR fixes have been applied.
import shutil
from os import environ

from dotenv import load_dotenv
load_dotenv()
environ.setdefault('PICKLED', 'true')

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.file_helper import EXTRACTED_EMAILS_DIR
from epstein_files.util.rich import console


for email in EpsteinFiles.get_files().emails:
    if email.is_local_extract_file():
        new_path = EXTRACTED_EMAILS_DIR.joinpath(email.filename)
        console.print(email.description())
        console.print(f'   Copying to "{new_path}"\n')
        shutil.copy2(email.file_path, new_path)
