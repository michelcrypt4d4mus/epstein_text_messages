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
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.util.constant.output_files import make_clean
from epstein_files.util.constant.strings import ID_REGEX
from epstein_files.util.data import flatten
from epstein_files.util.env import args
from epstein_files.util.file_helper import coerce_file_path, extract_file_id
from epstein_files.util.logging import exit_with_error, logger
from epstein_files.util.output import (print_emails_section, print_json_files, print_json_stats,
     print_other_files_section, print_text_messages_section, print_email_timeline, print_emailers_info,
     print_json_metadata, write_urls)
from epstein_files.util.rich import (build_highlighter, console, highlighter, print_color_key, print_json,
     print_title_page_header, print_title_page_tables, print_subtitle_panel, write_html)
from epstein_files.util.timer import Timer
from epstein_files.util.word_count import write_word_counts_html


def generate_html() -> None:
    if args.make_clean:
        make_clean()
        write_urls()
        exit()

    timer = Timer()
    epstein_files = EpsteinFiles.get_files(timer)

    if args.emailers_info:
        print_emailers_info(epstein_files)
        exit()
    elif args.json_metadata:
        print_json_metadata(epstein_files)
        exit()
    elif args.json_files:
        print_json_files(epstein_files)
        exit()

    print_title_page_header()

    if args.email_timeline:
        print_color_key()
    else:
        print_title_page_tables(epstein_files)

    if args.colors_only:
        exit()

    if args.output_texts:
        printed_logs = print_text_messages_section(epstein_files)
        timer.log_section_complete('MessengerLog', epstein_files.imessage_logs, printed_logs)

    if args.output_emails:
        printed_emails = print_emails_section(epstein_files)
        timer.log_section_complete('Email', epstein_files.emails, printed_emails)
    elif args.email_timeline:
        print_email_timeline(epstein_files)
        timer.print_at_checkpoint(f"Printed chronological emails table")

    if args.output_other:
        printed_files = print_other_files_section(epstein_files)
        timer.log_section_complete('OtherFile', epstein_files.other_files, printed_files)

    write_html(args.build)
    logger.warning(f"Total time: {timer.seconds_since_start_str()}")

    if args.debug:
        highlighter.print_highlight_counts(console)

    # JSON stats (mostly used for building pytest checks)
    if args.json_stats:
        print_json_stats(epstein_files)


def epstein_diff():
    """Diff the cleaned up text of two files."""
    Document.diff_files(args.positional_args)


def epstein_search():
    """Search the cleaned up text of the files."""
    epstein_files = EpsteinFiles.get_files()

    if ID_REGEX.match(args.positional_args[0]):
        logger.warning(f"'{args.positional_args[0]}' seems to be an ID, running epstein_show instead...")
        epstein_show()
        return

    for search_term in args.positional_args:
        temp_highlighter = build_highlighter(search_term)
        search_results = epstein_files.docs_matching(search_term, args.names)
        print_subtitle_panel(f"Found {len(search_results)} documents matching '{search_term}'")

        for search_result in search_results:
            document = search_result.document

            if (isinstance(document, Email) and not args.output_emails) \
                    or (isinstance(document, OtherFile) and not args.output_other) \
                    or (isinstance(document, MessengerLog) and not args.output_texts):
                document.warn(f"{type(document).__name__} Skipping search result...")
                continue
            elif document.is_duplicate():
                console.print('\n', document.duplicate_file_txt(), '\n')
                continue

            if args.whole_file:
                console.print(document)
            else:
                console.print(document.summary_panel())

                for matching_line in search_result.lines:
                    line_txt = matching_line.__rich__()
                    console.print(Padding(temp_highlighter(line_txt), INFO_PADDING), style='gray37')

            console.line()


def epstein_show():
    """Show the color highlighted file. If --raw arg is passed, show the raw text of the file as well."""
    raw_docs: list[Document] = []
    console.line()

    try:
        if args.names:
            people = EpsteinFiles.get_files().person_objs(args.names)
            raw_docs = [doc for doc in flatten([p.emails for p in people])]
        else:
            ids = [extract_file_id(arg) for arg in args.positional_args]
            raw_docs = [Document(coerce_file_path(id)) for id in ids]

        docs = Document.sort_by_timestamp([document_cls(doc)(doc.file_path) for doc in raw_docs])
    except Exception as e:
        exit_with_error(str(e))

    for doc in docs:
        console.print('\n', doc, '\n')

        if args.raw:
            console.print(Panel(Text("RAW: ").append(doc.summary()), expand=False, style=doc._border_style()))
            console.print(escape(doc.raw_text()), '\n')

            if isinstance(doc, Email):
                console.print(Panel(Text("actual_text: ").append(doc.summary()), expand=False, style=doc._border_style()))
                console.print(escape(doc._actual_text()), '\n')
                metadata = doc.metadata()
                metadata['is_word_count_worthy'] = doc.is_word_count_worthy()
                print_json(f"{doc.file_id} Metadata", metadata)


def epstein_word_count() -> None:
    write_word_counts_html()
