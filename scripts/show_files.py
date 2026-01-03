#!/usr/bin/env python
# Show the contents of filenames or ids passed as positional args
from os import environ

from dotenv import load_dotenv
load_dotenv()
environ.setdefault('PICKLED', 'true')

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.env import args
from epstein_files.util.file_helper import extract_file_id, id_str
from epstein_files.util.rich import console, print_panel, print_section_header


epstein_files = EpsteinFiles.get_files()
ids = [id_str(arg) if len(arg) <= 6 else extract_file_id(arg) for arg in args.positional_args]
docs = epstein_files.get_documents_with_ids(ids)
console.line()

for doc in docs:
    console.line()
    console.print(doc)
