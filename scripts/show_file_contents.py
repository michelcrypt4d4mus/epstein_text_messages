#!/usr/bin/env python
# Show the contents of filenames or ids passed as positional args
import sys

from rich.panel import Panel

from scripts.use_pickled import epstein_files
from epstein_files.documents.email import Email
from epstein_files.util.env import args
from epstein_files.util.file_helper import extract_file_id, id_str
from epstein_files.util.rich import console, print_panel, print_section_header


if not args.positional_args:
    console.print(f"\n  ERROR: No positional args!\n", style='red1')
    sys.exit()

ids = [id_str(arg) if len(arg) <= 6 else extract_file_id(arg) for arg in args.positional_args]
docs = epstein_files.get_documents_by_id(ids)
console.line()

for doc in docs:
    console.line()
    console.print(doc)
    console.line()
    console.print(Panel(f"*** {doc.url_slug} RAW ***", expand=False))
    console.print(doc.raw_text())

    if isinstance(doc, Email):
        console.line()
        console.print(Panel(f"*** {doc.url_slug} actual_text ***", expand=False))
        console.print(doc._actual_text())
