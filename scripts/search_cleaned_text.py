#!/usr/bin/env python
# Search the document text AFTER all OCR fixes have been applied.
import re
from os import environ
from sys import exit

from dotenv import load_dotenv
from rich.highlighter import RegexHighlighter
load_dotenv()
environ.setdefault('PICKLED', 'true')

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.env import args, specified_names
from epstein_files.util.highlighted_group import REGEX_STYLE_PREFIX
from epstein_files.util.rich import console, print_section_header


def build_highlighter(pattern: str) -> RegexHighlighter:
    class TempHighlighter(RegexHighlighter):
        """rich.highlighter that finds and colors interesting keywords based on the above config."""
        base_style = f"{REGEX_STYLE_PREFIX}."
        highlights = [re.compile(fr"(?P<lawyer>{pattern})", re.IGNORECASE)]

    return TempHighlighter()


if len(args.positional_args) == 0:
    console.print(f"Must provide an argument to search for.", style='bright_red')
    exit()

epstein_files = EpsteinFiles.get_files()

for search_term in args.positional_args:
    search_type = 'other' if args.search_other else 'all'
    print_section_header(f"Searching {search_type} documents for '{search_term}'")
    temp_highlighter = build_highlighter(search_term)

    for search_result in epstein_files.docs_matching(search_term, search_type, specified_names):
        console.line()

        if args.whole_file:
            console.print(search_result.document)
        else:
            console.print(search_result.document.description_panel())

            if search_result.document.hint_txt():
                console.line()

            for line in search_result.unprefixed_lines():
                console.print(temp_highlighter(line), style='wheat4')
