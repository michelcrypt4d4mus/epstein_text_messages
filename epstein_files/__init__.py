#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.

    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT epstein_generate'
"""
import re
from subprocess import check_output
from sys import exit

from dotenv import load_dotenv
load_dotenv()
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.epstein_files import EpsteinFiles, document_cls
from epstein_files.documents.document import INFO_PADDING, Document
from epstein_files.documents.documents.word_count import write_word_counts_html
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.output import (print_doj_files, print_emails_section, print_json_files,
     print_stats, print_other_files_section, print_text_messages_section, print_email_timeline,
     print_emailers_info, print_json_metadata, write_urls)
from epstein_files.output.rich import (build_highlighter, cfg_table, console, highlighter, print_color_key,
     print_json, print_title_page_header, print_title_page_tables, print_subtitle_panel, styled_key_value, write_html)
from epstein_files.util.constant.output_files import make_clean
from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_NOV_2025_ID_REGEX
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import flatten
from epstein_files.util.helpers.file_helper import extract_file_id
from epstein_files.util.logging import exit_with_error, logger
from epstein_files.util.timer import Timer


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

    if args.output_doj_files:
        printed_doj_files = print_doj_files(epstein_files)
        timer.log_section_complete('DojFile', epstein_files.doj_files, printed_doj_files)

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

    if args.stats:
        print_stats(epstein_files)  # Used for building pytest checks


def epstein_diff():
    """Diff the cleaned up text of two files."""
    Document.diff_files(args.positional_args)


def epstein_grep():
    """Search the cleaned up text of the files."""
    epstein_files = EpsteinFiles.get_files()

    if HOUSE_OVERSIGHT_NOV_2025_ID_REGEX.match(args.positional_args[0]):
        logger.warning(f"'{args.positional_args[0]}' seems to be an ID, running epstein_show instead...")
        epstein_show()
        return

    for search_term in args.positional_args:
        temp_highlighter = build_highlighter(search_term)
        search_results = epstein_files.docs_matching(search_term, args.names)
        print_subtitle_panel(f"Found {len(search_results)} documents matching '{search_term}'")
        last_document = None

        for search_result in search_results:
            doc = search_result.document.printable_document()
            lines = search_result.lines

            if (isinstance(doc, Email) and not args.output_emails) \
                    or (isinstance(doc, (DojFile, OtherFile)) and not args.output_other) \
                    or (isinstance(doc, MessengerLog) and not args.output_texts):
                doc.log(f"{type(doc).__name__} Skipping search result...")
                continue
            elif isinstance(doc, Email) and args.email_body:
                lines = [l for l in search_result.lines if l.line_number > doc.header.num_header_rows]

                if not lines:
                    doc.log(f"None of the matches for '{search_term}' seem to be in the body of the email")
                    continue

            if doc.is_duplicate:
                if last_document and not last_document.is_duplicate:
                    console.line()

                last_document = doc
                console.print(doc.duplicate_file_txt)
            elif args.whole_file:
                console.print(doc)
            else:
                console.print(doc.summary_panel)

                for matching_line in lines:
                    line_txt = matching_line.__rich__()
                    console.print(Padding(temp_highlighter(line_txt), INFO_PADDING), style='gray37')

            console.line()
            console.print(doc.locations, style='dim')
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
            ids = [extract_file_id(arg.upper().strip().strip('_')) for arg in args.positional_args]
            logger.info(f"extracted IDs: {ids}")
            raw_docs = [Document.from_file_id(id) for id in ids]
            logger.info(f"raw docs: {raw_docs}")

        # Rebuild the Document objs so we can see result of latest processing
        docs = Document.sort_by_timestamp([document_cls(doc)(doc.file_path) for doc in raw_docs])
        logger.info(f"Document types: {[doc._class_name for doc in docs]}")
    except Exception as e:
        console.print_exception()
        exit_with_error(str(e))

    for doc in docs:
        console.print('\n', doc)

        if args.raw:
            console.line()
            console.print(Panel(Text("RAW: ").append(doc.summary), expand=False, style=doc.border_style))
            console.print(escape(doc.raw_text()), '\n')

            if isinstance(doc, Email):
                console.print(Panel(Text("actual_text: ").append(doc.summary), expand=False, style=doc.border_style))
                console.print(escape(doc._extract_actual_text()), '\n')
                metadata = doc.metadata
                metadata['is_fwded_article'] = doc.is_fwded_article
                metadata['is_word_count_worthy'] = doc.is_word_count_worthy
                metadata['_is_first_for_user'] = doc._is_first_for_user
                print_json(f"{doc.file_id} Metadata", metadata)

        console.print(doc.debug_dict_txt, style='dim')

        # if args.debug and doc.config:
        #     console.line()
        #     console.print(styled_key_value('doc.is_interesting', doc.is_interesting, indent=39, sep=': '))
        #     console.print(cfg_table(doc.config))

        if args.open_pdf:
            check_output(['open', str(doc.locations.local_pdf_path)])
        if args.open_txt:
            check_output(['open', str(doc.file_path)])
        if args.open_url:
            check_output(['open', str(doc.external_url)])

def epstein_word_count() -> None:
    write_word_counts_html()
