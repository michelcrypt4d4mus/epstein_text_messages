#!/usr/bin/env python
# Show the contents of filenames or ids passed as positional args
import sys

from dotenv import load_dotenv
load_dotenv()
from rich.panel import Panel

from epstein_files.documents.document import Document
from epstein_files.documents.email import Email
from epstein_files.epstein_files import EpsteinFiles, document_cls
from epstein_files.util.env import args
from epstein_files.util.file_helper import coerce_file_path, extract_file_id
from epstein_files.util.rich import console, print_panel, print_section_header


if not args.positional_args:
    console.print(f"\n  ERROR: No positional args!\n", style='red1')
    sys.exit()

ids = [extract_file_id(arg) for arg in args.positional_args]
console.line()

if args.pickled:
    epstein_files = EpsteinFiles.get_files()
    docs = epstein_files.get_documents_by_id(ids)
else:
    raw_docs = [Document(coerce_file_path(id)) for id in ids]
    docs = [document_cls(doc)(doc.file_path) for doc in raw_docs]


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
