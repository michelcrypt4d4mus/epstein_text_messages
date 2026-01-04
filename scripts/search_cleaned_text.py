#!/usr/bin/env python
# Search the document text AFTER all OCR fixes have been applied.
import re
from sys import exit

from rich.padding import Padding

from scripts.use_pickled import epstein_files
from epstein_files.documents.document import INFO_PADDING
from epstein_files.util.env import args, specified_names
from epstein_files.util.highlighted_group import EpsteinHighlighter
from epstein_files.util.rich import console, print_panel


def build_highlighter(pattern: str) -> EpsteinHighlighter:
    class TempHighlighter(EpsteinHighlighter):
        """rich.highlighter that finds and colors interesting keywords based on the above config."""
        highlights = EpsteinHighlighter.highlights + [re.compile(fr"(?P<trump>{pattern})", re.IGNORECASE)]

    return TempHighlighter()


if len(args.positional_args) == 0:
    console.print(f"Must provide an argument to search for.", style='bright_red')
    exit()

for search_term in args.positional_args:
    temp_highlighter = build_highlighter(search_term)
    search_results = epstein_files.docs_matching(search_term, specified_names)
    console.line(2)
    print_panel(f"Found {len(search_results)} documents matching '{search_term}'", centered=True)

    for search_result in search_results:
        console.line()

        if args.whole_file:
            console.print(search_result.document)
        else:
            console.print(search_result.document.description_panel())

            for matching_line in search_result.lines:
                line_txt = matching_line.__rich__()
                console.print(Padding(temp_highlighter(line_txt), INFO_PADDING), style='gray37')
