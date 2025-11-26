#!/usr/bin/env python
# Search the document text AFTER all OCR fixes have been applied.
from os import environ
from sys import argv, exit
environ.setdefault('FAST', 'true')

from dotenv import load_dotenv
load_dotenv()
from rich.console import Console

from documents.document import Document
from documents.epstein_files import EpsteinFiles
from util.env import is_debug
from util.file_helper import DOCS_DIR
from util.rich import print_section_header


console = Console(color_system='256')
console.print(f"argv: {argv}")

if len(argv) == 1:
    console.print(f"Must provide an argument to search for.", style='bright_red')
    exit()

epstein_files = EpsteinFiles()

for search_term in argv[1:]:
    print_section_header(f"Searching for '{search_term}'")

    for line in epstein_files.lines_matching(search_term):
        console.print(line)
