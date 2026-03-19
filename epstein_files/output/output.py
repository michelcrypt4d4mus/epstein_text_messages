import json
from collections import defaultdict
from os import unlink
from subprocess import CalledProcessError, check_output
from typing import TypeVar

from rich import box
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

from epstein_files.documents.document import Document
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import FIRST_FEW_LINES, OtherFile
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.output.doc_printer import DocPrinter
from epstein_files.output.epstein_highlighter import highlighter
from epstein_files.output.rich import *
from epstein_files.output.site.internal_links import (AUTHORS_USING_SIGNATURES, FILES_THAT_ARE_NEITHER_EMAILS_NOR,
     HIS_EMAILS, HIS_TEXT_MESSAGES, SELECTIONS_FROM)
from epstein_files.output.site.sites import EMAILERS_TABLE_PNG_PATH, HtmlDir
from epstein_files.output.title_page import print_other_page_link, section_header
from epstein_files.people.interesting_people import EMAILERS_TO_PRINT
from epstein_files.people.names import *
from epstein_files.people.person import Person
from epstein_files.util.constant.html import HTML_TERMINAL_THEME, RICH_HTML_TEMPLATE
from epstein_files.util.constant.strings import AUTHOR
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import dict_sets_to_lists, uniq_sorted
from epstein_files.util.helpers.file_helper import file_size_str, log_file_write
from epstein_files.util.helpers.rich_helpers import join_texts
from epstein_files.util.helpers.string_helper import extract_emojis
from epstein_files.util.logging import logger, exit_with_error

DEVICE_SIGNATURE_PADDING = (1, 0)
PRINT_COLOR_KEY_EVERY_N_EMAILS = 150

OTHER_INTERESTING_EMAILS_SUBTITLE = 'Other Interesting Emails\n(these emails have been flagged as being of particular interest)'
CONVERSATIONS_SORTED_BY_TXT = Text("(conversations sorted chronologically based on timestamp of the first text message)", 'dim')
DEVICE_SIGNATURE_SUBTITLE = f"Email [italic]Sent from \\[DEVICE][/italic] Signature Breakdown"
DEVICE_SIGNATURE = 'Device Signature'

NOTES_TABLE_COLS = [
    {'name': 'ID', 'justify': 'left'},
    {'name': 'Type', 'justify': 'left'},
    {'name': 'Date', 'justify': 'left', 'style': TIMESTAMP_DIM},
    {'name': 'Author', 'justify': 'left', 'max_width': 20},
    # {'name': 'To', 'justify': 'left', 'min_width': min_width, 'max_width': max_width + 2},
    {'name': 'Note', 'justify': 'left', 'min_width': 32},
]

T = TypeVar('T')


def print_all_emails_chronological(epstein_files: EpsteinFiles, printer: DocPrinter) -> None:
    """Print all non-mailing list emails in chronological order."""
    emails = Document.sort_by_timestamp([e for e in epstein_files.unique_emails if not e.is_mailing_list])
    emails = _max_records(emails)
    title = f'Table of All {len(emails):,} Non-Junk Emails in Chronological Order (actual emails below)'
    table = Email.build_emails_table(emails, title=title, show_length=True)
    printer.print(Padding(table, (2, 0)))
    printer.print_section_subtitle('The Chronologically Ordered Emails')
    printer.print_documents(emails)


def print_curated_chronological(epstein_files: EpsteinFiles, printer: DocPrinter) -> None:
    """Print only interesting files of all types in chronological order."""
    logger.warning(f'Printing curated chronological site...')

    def should_print(doc: Document) -> bool:
        if doc._config.attached_to_email_id:
            return False
        else:
            return bool(doc.is_interesting if not args.invert_chrono else not doc.is_interesting)

    docs = [d for d in epstein_files.unique_documents if should_print(d)]
    printer.print_section_subtitle('Selected Files of Interest in Chronological Order')
    printer.print_documents(_max_records(docs))


def print_doj_files(epstein_files: EpsteinFiles, printer: DocPrinter) -> None:
    """Doesn't print DojFiles that are actually Emails, that's handled in print_emails()."""
    printer.collect_other_files_to_tables = False
    docs = Document.without_dupes(epstein_files.doj_files)
    printer.print_documents(_max_records(docs))


def print_emailers_info(epstein_files: EpsteinFiles) -> None:
    """Print tbe summary table of everyone who sent or received an email to a .png file."""
    printer = DocPrinter(epstein_files=epstein_files)
    printer.print_color_key()
    console.line()
    all_emailers = sorted(epstein_files.emailers, key=lambda person: person.sort_key)
    console.print(Person.emailer_info_table(all_emailers, show_epstein_total=True))

    if not args.build:
        logger.warning(f"Not writing .png file because --build is not set")
        return

    svg_path = f"{EMAILERS_TABLE_PNG_PATH}.svg"
    console.save_svg(svg_path, theme=HTML_TERMINAL_THEME, title="Epstein Emailers")
    log_file_write(svg_path)

    try:  # Inkscape is better at converting svg to png
        inkscape_cmd_args = ['inkscape', f'--export-filename={EMAILERS_TABLE_PNG_PATH}', svg_path]
        logger.warning(f"Running inkscape cmd: {' '.join(inkscape_cmd_args)}")
        check_output(inkscape_cmd_args)
    except (CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Failed to convert svg to png with inkscape, falling back to cairosvg: {e}")
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=str(EMAILERS_TABLE_PNG_PATH))

    log_file_write(EMAILERS_TABLE_PNG_PATH)
    unlink(svg_path)


def print_emails_section(epstein_files: EpsteinFiles, printer: DocPrinter) -> None:
    """
    Print emails grouped by participant with summary tables.
    Emails can be printed more than once (e.g. in the sender's section and each recipient's).
    """
    printer.print(section_header((SELECTIONS_FROM if not args.all_emails else '') + HIS_EMAILS))
    all_emailers = sorted(epstein_files.emailers, key=lambda person: person.earliest_email_at)
    num_since_color_key = 0

    if args.names:
        try:
            emailers_to_print = epstein_files.person_objs(args.names)
        except Exception as e:
            exit_with_error(str(e))
    else:
        emailers_to_print = all_emailers if args.all_emails else epstein_files.person_objs(EMAILERS_TO_PRINT)
        printer.print(_section_summary_table(Person.emailer_info_table(all_emailers, emailers_to_print)))

    for person in _max_records(emailers_to_print):
        if person.is_interesting is False and not args.names:
            logger.warning(f"Skipping person with is_interesting=False '{person.name}'")
            continue

        printed_emails = person.print_emails(printer)

        # Print color key every once in a while
        if (num_since_color_key := num_since_color_key + len(printed_emails)) > PRINT_COLOR_KEY_EVERY_N_EMAILS:
            printer.print_color_key()
            num_since_color_key = 0

    if args.names:
        return

    # Print other interesting emails
    extra_emails = [
        e for e in epstein_files.unique_emails
        if e.is_interesting and e.file_id not in printer.printed_ids
    ]

    if len(extra_emails) > 0:
        logger.warning(f"Found {len(extra_emails)} additional interesting emails by less interesting people...")
        printer.print_section_subtitle(OTHER_INTERESTING_EMAILS_SUBTITLE)
        printer.print_documents(Document.sort_by_timestamp(extra_emails))

    print_signatures_and_emojis(epstein_files, printer)
    fwded_articles = [e for e in printer.printed_emails if e.is_fwded_article]
    log_msg = f"Rewrote {len(Email.rewritten_header_ids)} of {len(printer.printed_emails)} email headers"
    logger.warning(f"  -> {log_msg}, {len(fwded_articles)} of the Emails printed were forwarded articles.")

    if args.all_emails:
        _verify_all_emails_were_printed(epstein_files, printer.printed_emails)


# NOTE: the JSON files from Nov. 2025 are completely uninteresting
def print_json_files(epstein_files: EpsteinFiles) -> None:
    """Print all the `JsonFile` objects to a unified JSON file."""
    if args.build:
        json_data = {jf.file_info.url_slug: jf.json_data() for jf in epstein_files.json_files}
        # TODO: stopgap so this doesn't break but we're no longer building this file.
        build_path = 'json_files.json' # SiteType.build_path('json_files')# SiteType.JSON_FILES)

        with open(build_path, 'wt') as f:
            f.write(json.dumps(json_data, sort_keys=True))
            log_file_write(build_path)
    else:
        for json_file in epstein_files.json_files:
            console.line(2)
            console.print(json_file._summary_panel)
            console.print_json(json_file.json_str(), indent=4, sort_keys=False)


def print_json_metadata(epstein_files: EpsteinFiles) -> None:
    """Print all our `DocCfg` and derived info about authorship etc."""
    if args.build:
        output_path = Site.html_output_path(Site.JSON_METADATA)

        with open(output_path, 'wt') as f:
            f.write(epstein_files.json_metadata())
            log_file_write(output_path)
    else:
        console.print_json(epstein_files.json_metadata(), indent=4, sort_keys=True)


def print_document_notes(epstein_files: EpsteinFiles, printer: DocPrinter) -> None:
    notes: list[Text] = []

    table = build_table(
        "Notes from The Epstein Files",
        cols=NOTES_TABLE_COLS,
        border_style=DEFAULT_TABLE_KWARGS['border_style'],
        header_style="bold",
        highlight=False,
        show_lines=True,
    )

    for doc in epstein_files.unique_documents:
        if not (doc.is_interesting and doc._config.note_txt):
            continue

        info = doc.formatted_info()
        row = [info.get(k, '') for k in ['file_id', 'short_type', 'date', 'author', 'note']]
        table.add_row(*row)
        notes.append(join_texts(row))

    table._no_pad = True  # hacky af
    printer.print(table)
    logger.warning(f"Printed {len(notes)} interesting documents with configured notes...")


def print_other_files_section(epstein_files: EpsteinFiles, printer: DocPrinter) -> list[OtherFile]:
    """Prints a table of `OtherFile` and returns the objects that were printed."""
    if args.uninteresting:
        files = [f for f in epstein_files.non_attachments if not f.is_interesting]
    else:
        files = [f for f in epstein_files.non_attachments if args.all_other_files or f.is_interesting]

    files = _max_records(Document.sort_by_timestamp(files))
    title_pfx = '' if args.all_other_files else 'Selected '
    category_table = OtherFile.summary_table(files, title_pfx=title_pfx)
    printer.print_section_subtitle(f"{FIRST_FEW_LINES} of {len(files)} {title_pfx}{FILES_THAT_ARE_NEITHER_EMAILS_NOR}")
    print_other_page_link(epstein_files)  # TODO: not in custom HTML
    printer.print(_section_summary_table(category_table))

    # If --all-other-files is enables, print the biographical panels, otherwise just print a big table
    if args.all_other_files:
        printer.print_documents(files, suppressed_as_normal=True)
    else:
        printer.print_centered(OtherFile.files_preview_table(files, title_pfx=title_pfx))

    return files


def print_signatures_and_emojis(epstein_files: EpsteinFiles, printer: DocPrinter) -> None:
    """Print device signatures and emojis and who used them."""
    printer.print_section_subtitle(DEVICE_SIGNATURE_SUBTITLE)
    printer.print(_signature_table(epstein_files.email_device_signatures_to_authors(), (DEVICE_SIGNATURE, AUTHOR), ', '))
    printer.print(_signature_table(epstein_files.email_authors_to_device_signatures(), (AUTHOR, DEVICE_SIGNATURE)))
    author_emojis = defaultdict(set)
    emoji_authors = defaultdict(set)

    for email in [e for e in epstein_files.emails if e.is_word_count_worthy]:
        if (emojis := extract_emojis(email.actual_text)):
            author_emojis[email.author].update(emojis)

            for emoji in emojis:
                emoji_authors[emoji].add(email.author_str)

    printer.line()
    printer.print_section_subtitle("Emoji Usage")
    printer.print_centered(_signature_table(emoji_authors, ('Emoji', AUTHOR)))


def print_stats(epstein_files: EpsteinFiles) -> None:
    """Used to generate fixture data for `pytest`."""
    console.print('\n\n\n', Panel('JSON Stats Dump', expand=True, style='reverse bold'), '\n')
    print_json(MessengerLog.count_authors(epstein_files.imessage_logs), f"MessengerLog Sender Counts", skip_falsey=True)
    print_json(epstein_files.email_author_counts(), f"Email Author Counts", skip_falsey=True)
    print_json(epstein_files.email_recipient_counts(), f"Email Recipient Counts", skip_falsey=True)
    print_json(epstein_files.email_signature_substitution_counts(), "Email signature_substitution_countss", skip_falsey=True)
    print_json(dict_sets_to_lists(epstein_files.email_authors_to_device_signatures()), "Email author device signatures")
    print_json(dict_sets_to_lists(epstein_files.email_device_signatures_to_authors()), "Email authors by device")
    unknown_recipient_ids = sorted([e.file_id for e in epstein_files.emails if None in e.recipients or not e.recipients])
    print_json(unknown_recipient_ids, "Unknown Recipient IDs")
    print_json(Document.count_by_month(epstein_files.documents), "All documents count by month")
    print_json(sorted([f.file_id for f in epstein_files.interesting_other_files]), "Interesting OtherFile IDs")
    print_json(highlighter.highlight_counts, f"Highlight Counts")
    print_json(epstein_files.counterparties_dict, f"Counterparties")
    highlighter.print_highlight_counts(console)


def print_text_msgs_section(epstein_files: EpsteinFiles, printer: DocPrinter) -> None:
    """Print `MessengerLog` objects and return objects that were printed."""
    section_header_panel = section_header((SELECTIONS_FROM if not args.all_texts else '') + HIS_TEXT_MESSAGES)
    printer.print(section_header_panel)
    printer.print(Align.center(CONVERSATIONS_SORTED_BY_TXT))

    if args.names:
        imessage_logs = [log for log in epstein_files.imessage_logs if log.author in args.names]
    else:
        imessage_logs = [log for log in epstein_files.imessage_logs if args.all_texts or log.is_interesting]

    imessage_logs = _max_records(imessage_logs)

    if not imessage_logs:
        logger.warning(f"No MessengerLog found for {args.names}")
        return

    if not args.names:
        printer.print(_section_summary_table(MessengerLog.summary_table(imessage_logs)))

    printer.print_documents(imessage_logs)


def show_urls() -> None:
    """Print the various URLs generated by this code."""
    try:
        urls = {
            k: Text('[', 'grey30').append(file_size_str(Site.html_output_path(k), 1), 'cyan').append('] ') + \
                Text(v, ARCHIVE_LINK_COLOR)
            for k, v in Site.all_urls().items()
        }
    except FileNotFoundError:
        urls = Site.all_urls()

    console.print(Padding(styled_dict(urls), (1)))


def write_html(output_path: Path | Site | None, **kwargs) -> Path | None:
    """
    Write all `console` output to HTML in `output_path` (if provided).
    If `args.write_txt` is set colored ANSI `.txt` files will be written instead.
    Returns the path that was written (if any).
    """
    if not output_path:
        logger.warning(f"Not writing HTML (args.build={args.build}, args._site={args._site}.")
        return
    elif isinstance(output_path, Site):
        output_path = Site.html_output_path(output_path)

    if args.write_txt:
        output_path = HtmlDir.build_path(f"{output_path.stem}.txt")
        console.save_text(str(output_path))
    else:
        console.save_html(
            str(output_path),
            clear=False,
            code_format=str(RICH_HTML_TEMPLATE),
            theme=HTML_TERMINAL_THEME,
            **kwargs
        )

    log_file_write(output_path)
    return output_path


def _section_summary_table(table: Table) -> Align:
    return Align(Padding(table, (1, 0, 1, 0)), 'center')


def _signature_table(keyed_sets: dict[str, set[str]], cols: tuple[str, str], join_char: str = '\n') -> Padding:
    """Build table for who signed emails with 'Sent from my iPhone' etc."""
    new_dict = dict_sets_to_lists(keyed_sets)

    if cols[0] == AUTHOR:
        if cols[1] == DEVICE_SIGNATURE:
            title = 'Email Signatures Used By Authors'
        else:
            title = f"{cols[1]} used by Authors"
    else:
        title = AUTHORS_USING_SIGNATURES

    table = build_table(title, header_style="bold reverse", show_lines=True)

    for i, col in enumerate(cols):
        table.add_column(col.title() + ('s' if i == 1 else ''))

    for k in sorted(new_dict.keys()):
        table.add_row(highlighter(k or UNKNOWN), highlighter(join_char.join(sorted(new_dict[k]))))

    return Padding(table, DEVICE_SIGNATURE_PADDING)


def _verify_all_emails_were_printed(epstein_files: EpsteinFiles, printed_emails: list[Email]) -> None:
    """Log warnings if some emails were never printed."""
    email_ids_that_were_printed = set([email.file_id for email in printed_emails])
    logger.warning(f"Printed {len(printed_emails):,} emails of {len(email_ids_that_were_printed):,} unique file IDs.")
    missed_an_email = False

    for email in epstein_files.unique_emails:
        if email.file_id not in email_ids_that_were_printed:
            logger.error(f"Failed to print {email._summary}")
            missed_an_email = True

    if not missed_an_email:
        logger.warning(f"All {len(epstein_files.emails):,} emails printed at least once.")


def _max_records(docs: list[T]) -> list[T]:
    """Truncate number of Documents if `args.max_records` is specified."""
    if args.max_records and args.max_records < len(docs):
        logger.warning(f"Truncating to args.max_records={args.max_records} objects...")
        return docs[0:args.max_records]
    else:
        return docs
