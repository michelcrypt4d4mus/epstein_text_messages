#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_

Install: 'poetry install'
    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT ./generate.py'
"""
from sys import exit

from dotenv import load_dotenv
load_dotenv()

from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel

from epstein_files.epstein_files import EpsteinFiles, document_cls
from epstein_files.documents.document import INFO_PADDING, Document
from epstein_files.documents.email import Email
from epstein_files.util.constant.html import *
from epstein_files.util.constant.names import *
from epstein_files.util.env import args, specified_names
from epstein_files.util.file_helper import GH_PAGES_HTML_PATH, coerce_file_path, extract_file_id, make_clean
from epstein_files.util.logging import logger
from epstein_files.util.output import print_emails, print_json_metadata, print_json_stats, print_text_messages
from epstein_files.util.rich import build_highlighter, console, print_header, print_panel, write_html
from epstein_files.util.timer import Timer


def generate_html() -> None:
    if args.make_clean:
        make_clean()
        exit()

    timer = Timer()
    epstein_files = EpsteinFiles.get_files(timer)

    if args.json_metadata:
        print_json_metadata(epstein_files)
        exit()

    print_header(epstein_files)

    if args.colors_only:
        exit()

    if args.output_texts:
        print_text_messages(epstein_files)
        timer.print_at_checkpoint(f'Printed {len(epstein_files.imessage_logs)} text message logs')

    if args.output_emails:
        emails_printed = print_emails(epstein_files)
        timer.print_at_checkpoint(f"Printed {emails_printed:,} emails")

    if args.output_other_files:
        files_printed = epstein_files.print_other_files_table()
        timer.print_at_checkpoint(f"Printed {len(files_printed)} other files")

    # Save output
    write_html(GH_PAGES_HTML_PATH)
    logger.warning(f"Total time: {timer.seconds_since_start_str()}")

    # JSON stats (mostly used for building pytest checks)
    if args.json_stats:
        print_json_stats(epstein_files)


def epstein_search():
    """Search the cleaned up text of the files."""
    _assert_positional_args()
    epstein_files = EpsteinFiles.get_files(use_pickled=True)

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


def epstein_show():
    """Show the color highlighted file. If --raw arg is passed, show the raw text of the file as well."""
    _assert_positional_args()
    ids = [extract_file_id(arg) for arg in args.positional_args]
    console.line()

    if args.pickled:
        epstein_files = EpsteinFiles.get_files(use_pickled=True)
        docs = epstein_files.get_documents_by_id(ids)
    else:
        raw_docs = [Document(coerce_file_path(id)) for id in ids]
        docs = [document_cls(doc)(doc.file_path) for doc in raw_docs]

    for doc in docs:
        console.line()
        console.print(doc)

        if args.raw:
            console.line()
            console.print(Panel(f"*** {doc.url_slug} RAW ***", expand=False, style=doc._border_style()))
            console.print(escape(doc.raw_text()))

            if isinstance(doc, Email):
                console.line()
                console.print(Panel(f"*** {doc.url_slug} actual_text ***", expand=False, style=doc._border_style()))
                console.print(escape(doc._actual_text()))


def _assert_positional_args():
    if not args.positional_args:
        console.print(f"\n  ERROR: No positional args!\n", style='red1')
        exit(1)
