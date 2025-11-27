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
from util.rich import print_section_header


console = Console(color_system='256')

if len(args.search) == 0 and len(args.search_other) == 0:
    console.print(f"Must provide an argument to search for.", style='bright_red')
    exit()

epstein_files = EpsteinFiles()

for search_term in args.search:
    print_section_header(f"Searching for '{search_term}'")

    for line in epstein_files.lines_matching(search_term):
        console.print(line)

for search_term in args.search_other:
    print_section_header(f"Searching other files for '{search_term}'")

    for line in epstein_files.lines_matching(search_term, 'other'):
        console.print(line)
