#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.

    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT epstein_generate'
"""
from sys import exit

from dotenv import load_dotenv
load_dotenv()
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.epstein_files import EpsteinFiles, document_cls
from epstein_files.documents.document import INFO_PADDING, Document
from epstein_files.documents.email import Email
from epstein_files.util.constant.output_files import ALL_EMAILS_PATH, TEXT_MSGS_HTML_PATH, make_clean
from epstein_files.util.env import args, specified_names
from epstein_files.util.file_helper import coerce_file_path, extract_file_id
from epstein_files.util.logging import logger
from epstein_files.util.output import (print_emails_section, print_json_files, print_json_stats,
     print_other_files_section, print_text_messages_section, write_json_metadata, write_urls)
from epstein_files.util.rich import build_highlighter, console, print_header, print_panel, write_html
from epstein_files.util.timer import Timer
from epstein_files.util.word_count import write_word_counts_html


def generate_html() -> None:
    if args.make_clean:
        make_clean()
        write_urls()
        exit()

    timer = Timer()
    epstein_files = EpsteinFiles.get_files(timer)

    if args.json_metadata:
        write_json_metadata(epstein_files)
        exit()
    elif args.json_files:
        print_json_files(epstein_files)
        exit()

    print_header(epstein_files)

    if args.colors_only:
        exit()

    if args.output_texts:
        print_text_messages_section(epstein_files)
        timer.print_at_checkpoint(f'Printed {len(epstein_files.imessage_logs)} text message logs')

    if args.output_emails:
        emails_that_were_printed = print_emails_section(epstein_files)
        timer.print_at_checkpoint(f"Printed {len(emails_that_were_printed):,} emails")

    if args.output_other:
        if args.uninteresting:
            files = [f for f in epstein_files.other_files if not f.is_interesting()]
        else:
            files = [f for f in epstein_files.other_files if args.all_other_files or f.is_interesting()]

        print_other_files_section(files, epstein_files)
        timer.print_at_checkpoint(f"Printed {len(files)} other files (skipped {len(epstein_files.other_files) - len(files)})")

    # Save output
    write_html(ALL_EMAILS_PATH if args.all_emails else TEXT_MSGS_HTML_PATH)
    logger.warning(f"Total time: {timer.seconds_since_start_str()}")

    # JSON stats (mostly used for building pytest checks)
    if args.json_stats:
        print_json_stats(epstein_files)


def epstein_diff():
    """Diff the cleaned up text of two files."""
    Document.diff_files(args.positional_args)


def epstein_search():
    """Search the cleaned up text of the files."""
    _assert_positional_args()
    epstein_files = EpsteinFiles.get_files()

    for search_term in args.positional_args:
        temp_highlighter = build_highlighter(search_term)
        search_results = epstein_files.docs_matching(search_term, specified_names)
        console.line(2)
        print_panel(f"Found {len(search_results)} documents matching '{search_term}'", padding=(0, 0, 0, 3))

        for search_result in search_results:
            console.line()

            if args.whole_file:
                if isinstance(search_result.document, Email):
                    search_result.document._truncation_allowed = False

                console.print(search_result.document)
            else:
                console.print(search_result.document.summary_panel())

                for matching_line in search_result.lines:
                    line_txt = matching_line.__rich__()
                    console.print(Padding(temp_highlighter(line_txt), INFO_PADDING), style='gray37')


def epstein_show():
    """Show the color highlighted file. If --raw arg is passed, show the raw text of the file as well."""
    _assert_positional_args()
    ids = [extract_file_id(arg) for arg in args.positional_args]
    raw_docs = [Document(coerce_file_path(id)) for id in ids]
    docs = [document_cls(doc)(doc.file_path) for doc in raw_docs]
    console.line()

    for doc in docs:
        if isinstance(doc, Email):
            doc._truncation_allowed = False

        console.print('\n', doc, '\n')

        if args.raw:
            console.print(Panel(Text("RAW: ").append(doc.summary()), expand=False, style=doc._border_style()))
            console.print(escape(doc.raw_text()), '\n')

            if isinstance(doc, Email):
                console.print(Panel(Text("actual_text: ").append(doc.summary()), expand=False, style=doc._border_style()))
                console.print(escape(doc._actual_text()), '\n')


def epstein_word_count() -> None:
    write_word_counts_html()


def _assert_positional_args():
    if not args.positional_args:
        console.print(f"\n  ERROR: No positional args!\n", style='red1')
        exit(1)
