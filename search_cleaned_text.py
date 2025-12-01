#!/usr/bin/env python
# Search the document text AFTER all OCR fixes have been applied.
from os import environ
from sys import argv, exit
environ.setdefault('FAST', 'true')

from dotenv import load_dotenv
load_dotenv()
from rich.console import Console

from documents.epstein_files import EpsteinFiles
from util.env import args
from util.rich import console, print_section_header


if len(args.positional_args) == 0:
    console.print(f"Must provide an argument to search for.", style='bright_red')
    exit()

epstein_files = EpsteinFiles()

for search_term in args.positional_args:
    search_type = 'other' if args.search_other else 'all'
    print_section_header(f"Searching {search_type} documents for '{search_term}'")

    for line in epstein_files.lines_matching(search_term, search_type):
        console.print(line)
