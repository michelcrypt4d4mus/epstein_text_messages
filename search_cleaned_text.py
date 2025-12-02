#!/usr/bin/env python
# Search the document text AFTER all OCR fixes have been applied.
from os import environ
from sys import argv, exit
environ.setdefault('FAST', 'true')

from dotenv import load_dotenv
load_dotenv()
from rich.console import Console
from rich.panel import Panel

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

    for search_result in epstein_files.docs_matching(search_term, search_type):
        console.line(2)
        console.print(Panel(search_result.document.description(), expand=False))

        for line in search_result.lines:
            console.print(line)
