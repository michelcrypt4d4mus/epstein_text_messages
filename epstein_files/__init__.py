#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.

    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT epstein_generate'
"""
import itertools
import sys
from pathlib import Path
from subprocess import check_output

from dotenv import load_dotenv
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text
load_dotenv()

from epstein_files.epstein_files import EpsteinFiles, document_cls
from epstein_files.documents.document import Document
from epstein_files.documents.documents.word_count import print_word_counts
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.doc_printer import DocPrinter
from epstein_files.output.epstein_highlighter import highlighter, temp_highlighter
from epstein_files.output.output import (print_curated_chronological, print_doj_files, print_emails_section,
     print_json_files, print_stats, print_other_files_section, print_text_msgs_section, print_all_emails_chronological,
     print_signatures_and_emojis, print_emailers_info, print_json_metadata, show_urls)
from epstein_files.output.rich import console, print_json, print_subtitle_panel
from epstein_files.output.site.sites import Site, make_clean, use_custom_html
from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_NOV_2025_ID_REGEX
from epstein_files.util.constants import ALL_CONFIGS
from epstein_files.util.env import BUILD_TO_DEFAULT, args, site_config
from epstein_files.util.helpers.data_helpers import flatten, uniquify
from epstein_files.util.helpers.document_helper import diff_documents
from epstein_files.util.helpers.file_helper import extract_file_id, is_local_extract_file, open_file_or_url
from epstein_files.util.logging import exit_with_error, logger
from epstein_files.util.timer import Timer


def epstein_generate() -> None:
    timer, epstein_files = _load_files_and_check_early_exit_args()
    printer = DocPrinter(epstein_files=epstein_files)
    printer.print_title_page_top()

    if args.all_emails_chrono or args.output_bios or args.output_devices or args.output_word_count:
        printer.print_color_key()
    else:
        printer.print_title_page_bottom()

    if args.colors_only:
        pass
    elif args.output_bios:
        printer.print_biographies()
    elif args.output_devices:
        print_signatures_and_emojis(epstein_files, printer)
    elif args.output_chrono:
        logger.warning(f'Printing chronological site...')
        print_curated_chronological(epstein_files, printer)
        timer.log_section_complete('Document', epstein_files.unique_documents, printer.printed_docs)
    elif args.output_word_count:
        print_word_counts(epstein_files)
        timer.print_at_checkpoint(f"Finished counting words")
    elif args.all_doj_files:
        printed_doj_files = print_doj_files(epstein_files, printer)
        timer.log_section_complete('DojFile', epstein_files.doj_files, printed_doj_files)
    else:
        if args.output_emails:
            print_emails_section(epstein_files, printer)
            timer.log_section_complete('Email', epstein_files.emails, printer.printed_docs)
        elif args.all_emails_chrono:
            print_all_emails_chronological(epstein_files, printer)
            timer.log_section_complete('Chronological Email', epstein_files.emails, printer.printed_docs)

        if args.output_texts:
            printed_logs = print_text_msgs_section(epstein_files, printer)
            timer.log_section_complete('MessengerLog', epstein_files.imessage_logs, printed_logs)

        if args.output_other:
            printed_files = print_other_files_section(epstein_files, printer)
            timer.log_section_complete('OtherFile', epstein_files.other_files, printed_files)

    if args.build:
        write_html_arg = args._site if args.build == BUILD_TO_DEFAULT else Path(args.build)
        printer.write_html(write_html_arg)

    logger.warning(f"Total time: {timer.seconds_since_start_str()}")

    if args.names:
        Document._print_ids(printer.printed_docs, 'args.names')

    if args.open_txt:
        open_file_or_url(Site.custom_html_build_path(args._site))

    if args.stats:
        print_stats(epstein_files)  # Used for building pytest checks


def epstein_diff():
    """Diff the cleaned up text of two files."""
    diff_documents(args.positional_args)


def epstein_grep():
    """Search the cleaned up text of the files."""
    epstein_files = EpsteinFiles.get_files()

    if HOUSE_OVERSIGHT_NOV_2025_ID_REGEX.match(args.positional_args[0]):
        logger.warning(f"'{args.positional_args[0]}' seems to be an ID, running epstein_show instead...")
        epstein_show()
        return

    for search_term in args.positional_args:
        tmp_highlight = temp_highlighter(search_term, 'reverse')
        search_results = epstein_files.grep_documents(search_term, args.names)
        search_results = sorted(search_results, key=lambda sr: sr.document.timestamp_sort_key)
        print_subtitle_panel(f"Found {len(search_results)} documents matching '{search_term}'")
        last_document = None

        for search_result in search_results:
            doc = search_result.document
            lines = search_result.lines

            if (isinstance(doc, Email) and not args.output_emails) \
                    or (isinstance(doc, (DojFile, OtherFile)) and not args.output_other) \
                    or (isinstance(doc, MessengerLog) and not args.output_texts):
                doc._log(f"{type(doc).__name__} Skipping search result...")
                continue
            elif isinstance(doc, Email) and args.email_body:
                lines = [l for l in search_result.lines if l.line_number > doc.header.num_header_rows]

                if not lines:
                    doc._log(f"None of the matches for '{search_term}' seem to be in the body of the email")
                    continue

            if doc.is_duplicate:
                if last_document and not last_document.is_duplicate:
                    console.line()

                last_document = doc
                console.print(doc.duplicate_file_txt)
            elif args.whole_file:
                console.print(doc)
            else:
                console.print(doc._summary_panel)

                for matching_line in lines:
                    line_txt = matching_line.__rich__()
                    console.print(Padding(tmp_highlight(line_txt), site_config.info_padding()), style='gray37')

            console.line()

            if args.debug:
                console.print(doc._debug_txt(), style='dim')
                console.line()

        matched_ids = [result.document.file_id for result in search_results]
        txt = Text("\n\n'").append(search_term, style='bright_red').append("'").append(' matched IDs: ')
        console.print(txt.append(' '.join(matched_ids), style='cyan'))

        if args.repair:
            epstein_files.repair_ids(matched_ids)


def epstein_pdf_path():
    """Print the path to PDF with ID specified in first positional argument."""
    file_id = args.positional_args[0]
    assert file_id, "No ID provided!"
    assert file_id.startswith('EFTA'), f"{file_id} doesn't look like a valid EFTA file id..."
    document = EpsteinFiles.get_files().get_id(file_id)

    if not (document and document.file_info.local_pdf_path):
        logger.error(f"No PDF path found for {file_id}")

    print(document.file_info.local_pdf_path)


def epstein_show():
    """Show the color highlighted file. If --raw arg is passed, show the raw text of the file as well."""
    ids_with_attachments = set([c.attached_to_email_id for c in ALL_CONFIGS])
    epstein_files: EpsteinFiles | None = None
    raw_docs: list[Document] = []
    console.line()
    ids = []

    try:
        if args.names:
            people = EpsteinFiles.get_files().person_objs(args.names)
            raw_docs = [doc for doc in flatten([p.emails for p in people])]
        else:
            ids = [extract_file_id(arg.upper().strip().strip('_')) for arg in args.positional_args]
            with_attachment_ids = list(set(ids).intersection(ids_with_attachments))
            local_extract_ids = [id for id in ids if is_local_extract_file(id)]
            raw_docs = [Document.from_file_id(id) for id in ids if not is_local_extract_file(id)]

            if local_extract_ids or with_attachment_ids:
                epstein_files = EpsteinFiles.get_files()

                if local_extract_ids:
                    raw_docs += epstein_files.get_ids(local_extract_ids)

                # show the attachments bc reloaded obj won't have them
                for id in with_attachment_ids:
                    existing_doc = epstein_files.get_id(id)
                    logger.warning(f"Showing the attachments now because reloaded Email won't have them:")
                    console.print(existing_doc)

        if any(doc.file_info.has_file for doc in raw_docs):
            # Rebuild the Document objs so we can see result of latest processing
            docs = Document.sort_by_timestamp([document_cls(doc)(doc.file_path) for doc in raw_docs])
        else:
            logger.warning(f"Not reloading derived documents")
            docs = raw_docs

        logger.info(f"Found file IDs {ids} with types: {[doc._class_name for doc in docs]}")
    except FileNotFoundError as e:
        epstein_files = epstein_files or EpsteinFiles.get_files()

        if ids and (docs := epstein_files.get_ids(ids)):
            console.line(2)
            logger.error(f"Failed to find local file but found doc by id: {e}")
        else:
            exit_with_error(str(e))
    except Exception as e:
        console.print_exception()
        exit_with_error(str(e))

    for doc in docs:
        if args.open_pdf and doc.file_info.is_doj_file:
            doc.file_info.open_pdf()
        if args.open_txt:
            doc.file_info.open()
        if args.open_url:
            check_output(['open', str(doc.file_info.external_url)])

        if args.raw:
            console.line()
            console.print(Panel(Text(f"RAW {doc.file_id} RAW").append(doc._summary), expand=False, style=doc.border_style))
            console.print(escape(doc.raw_text()), '\n')

            if args.deep_debug:
                console.print(Panel(Text(f"LINES {doc.file_id} LINES")))
                print(doc._numbered_lines() + '\n\n')

            if isinstance(doc, Email):
                console.print(Panel(Text("actual_text: ").append(doc._summary), expand=False, style=doc.border_style))
                console.print(escape(doc._extract_actual_text()), '\n')

        console.print('\n', doc)

        if args.debug:
            console.print(doc._debug_txt(), style='dim')

    if args.stats:
        print_json(highlighter.highlight_counts, "Highlight counts")


def _load_files_and_check_early_exit_args() -> tuple[Timer, EpsteinFiles]:
    if args.make_clean:
        make_clean()
    elif args.show_urls:
        show_urls()
    elif args.use_custom_html:
        use_custom_html()
    else:
        timer = Timer()
        epstein_files = EpsteinFiles.get_files(timer)

        if args.emailers_info:
            print_emailers_info(epstein_files)
        elif args.json_metadata:
            print_json_metadata(epstein_files)
        elif args.json_files:
            print_json_files(epstein_files)
        elif args.repair:
            epstein_files.repair_ids(args.positional_args)
        else:
            return timer, epstein_files

    sys.exit()
