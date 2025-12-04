#!/usr/bin/env python
# Search the document text AFTER all OCR fixes have been applied.
from os import environ
from sys import argv, exit

from dotenv import load_dotenv
from rich.panel import Panel
load_dotenv()
environ.setdefault('PICKLE', 'true')

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.env import args
from epstein_files.util.rich import console, print_section_header


if len(args.positional_args) == 0:
    console.print(f"Must provide an argument to search for.", style='bright_red')
    exit()

epstein_files = EpsteinFiles.get_files()

for search_term in args.positional_args:
    search_type = 'other' if args.search_other else 'all'
    print_section_header(f"Searching {search_type} documents for '{search_term}'")

    for search_result in epstein_files.docs_matching(search_term, search_type):
        console.line()
        console.print(Panel(search_result.document.description(), expand=False))

        for line in search_result.unprefixed_lines():
            console.print(line)
