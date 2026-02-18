import json
from os import unlink
from subprocess import CalledProcessError, check_output
from typing import cast

from rich.padding import Padding

from epstein_files.documents.document import Document
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import FIRST_FEW_LINES, OtherFile
from epstein_files.epstein_files import EpsteinFiles, count_by_month
from epstein_files.output.rich import *
from epstein_files.output.title_page import (print_color_key, print_other_page_link, print_section_header,
     print_section_summary_table)
from epstein_files.people.interesting_people import EMAILERS_TO_PRINT
from epstein_files.people.person import Person
from epstein_files.util.constant.html import CONSOLE_HTML_FORMAT, HTML_TERMINAL_THEME, PAGE_TITLE
from epstein_files.util.constant.names import *
from epstein_files.output.sites import EMAILERS_TABLE_PNG_PATH
from epstein_files.util.constant.strings import AUTHOR
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import dict_sets_to_lists
from epstein_files.util.helpers.file_helper import file_size_str, log_file_write
from epstein_files.util.logging import logger, exit_with_error

DEVICE_SIGNATURE_SUBTITLE = f"Email [italic]Sent from \\[DEVICE][/italic] Signature Breakdown"
DEVICE_SIGNATURE = 'Device Signature'
DEVICE_SIGNATURE_PADDING = (1, 0)
OTHER_INTERESTING_EMAILS_SUBTITLE = 'Other Interesting Emails\n(these emails have been flagged as being of particular interest)'
PRINT_COLOR_KEY_EVERY_N_EMAILS = 150


def print_curated_chronological(epstein_files: EpsteinFiles) -> list[Document]:
    other_files_queue = []  # Collect other files into tables
    printed_docs: list[Document] = []

    for doc in epstein_files.unique_documents:
        if not doc.is_interesting:
            continue
        elif isinstance(doc, OtherFile):
            other_files_queue.append(doc)
            continue
        elif other_files_queue:
            console.print(Padding(OtherFile.files_preview_table(other_files_queue), (0, 0, 1, 2)))
            printed_docs.extend(other_files_queue)
            other_files_queue = []

        console.print(doc)
        printed_docs.append(doc)

    return printed_docs


def print_doj_files(epstein_files: EpsteinFiles) -> list[DojFile | Email]:
    """Doesn't print DojFiles that are actually Emails, that's handled in print_emails()."""
    printed_doj_files: list[DojFile | Email] = []
    last_was_empty = False

    for doj_file in epstein_files.doj_files:
        if isinstance(doj_file, DojFile) and (doj_file.is_empty or doj_file.is_bad_ocr):
            console.print(doj_file.empty_file_msg, style='dim')
            last_was_empty = True
            continue
        elif doj_file.is_duplicate:
            console.print(doj_file.duplicate_file_txt_padded)
            continue

        if last_was_empty:
            console.line()

        console.print(doj_file)
        last_was_empty = False
        printed_doj_files.append(doj_file)

    return printed_doj_files


def print_email_timeline(epstein_files: EpsteinFiles) -> None:
    """Print a table of all emails in chronological order."""
    emails = Document.sort_by_timestamp([e for e in epstein_files.unique_emails if not e.is_mailing_list])
    title = f'Table of All {len(emails):,} Non-Junk Emails in Chronological Order (actual emails below)'
    table = Email.build_emails_table(emails, title=title, show_length=True)
    console.print(Padding(table, (2, 0)))
    print_subtitle_panel('The Chronologically Ordered Emails')
    console.line()

    for email in emails:
        console.print(email)


def print_emailers_info(epstein_files: EpsteinFiles) -> None:
    """Print tbe summary table of everyone who sent or received an email to a .png file."""
    print_color_key()
    console.line()
    all_emailers = sorted(epstein_files.emailers, key=lambda person: person.sort_key)
    console.print(Person.emailer_info_table(all_emailers, show_epstein_total=True))

    if not args.build:
        logger.warning(f"Not writing .png file because --build is not set")
        return

    svg_path = f"{EMAILERS_TABLE_PNG_PATH}.svg"
    console.save_svg(svg_path, theme=HTML_TERMINAL_THEME, title="Epstein Emailers")
    log_file_write(svg_path)

    try:
        # Inkscape is better at converting svg to png
        inkscape_cmd_args = ['inkscape', f'--export-filename={EMAILERS_TABLE_PNG_PATH}', svg_path]
        logger.warning(f"Running inkscape cmd: {' '.join(inkscape_cmd_args)}")
        check_output(inkscape_cmd_args)
    except (CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Failed to convert svg to png with inkscape, falling back to cairosvg: {e}")
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=str(EMAILERS_TABLE_PNG_PATH))

    log_file_write(EMAILERS_TABLE_PNG_PATH)
    unlink(svg_path)


def print_emails_section(epstein_files: EpsteinFiles) -> list[Email]:
    """Prints emails, returns emails that were printed (may return dupes if printed for both author and recipient)."""
    print_section_header(('Selections from ' if not args.all_emails else '') + 'His Emails')
    print_other_page_link(epstein_files)
    all_emailers = sorted(epstein_files.emailers, key=lambda person: person.earliest_email_at)
    all_emails = Person.emails_from_people(all_emailers)
    num_emails_printed_since_last_color_key = 0
    printed_emails: list[Email] = []
    people_to_print: list[Person]

    if args.names:
        try:
            people_to_print = epstein_files.person_objs(args.names)
        except Exception as e:
            exit_with_error(str(e))
    else:
        if args.all_emails:
            people_to_print = all_emailers
        else:
            people_to_print = epstein_files.person_objs(EMAILERS_TO_PRINT)

        print_section_summary_table(Person.emailer_info_table(all_emailers, people_to_print))

    for person in people_to_print:
        if person.name in epstein_files.uninteresting_emailers and not args.names:
            continue

        printed_person_emails = person.print_emails()
        printed_emails.extend(printed_person_emails)
        num_emails_printed_since_last_color_key += len(printed_person_emails)

        # Print color key every once in a while
        if num_emails_printed_since_last_color_key > PRINT_COLOR_KEY_EVERY_N_EMAILS:
            print_color_key()
            num_emails_printed_since_last_color_key = 0

    if args.names:
        return printed_emails

    # Print other interesting emails
    printed_email_ids = [email.file_id for email in printed_emails]
    extra_emails = [e for e in all_emails if e.is_interesting and e.file_id not in printed_email_ids]
    logger.warning(f"Found {len(extra_emails)} extra_emails...")

    if len(extra_emails) > 0:
        print_subtitle_panel(OTHER_INTERESTING_EMAILS_SUBTITLE)
        console.line()

        for other_email in Document.sort_by_timestamp(extra_emails):
            console.print(other_email)
            printed_emails.append(cast(Email, other_email))

    if args.all_emails:
        _verify_all_emails_were_printed(epstein_files, printed_emails)

    _print_email_device_signature_info(epstein_files)
    fwded_articles = [e for e in printed_emails if e.config and e.is_fwded_article]
    log_msg = f"Rewrote {len(Email.rewritten_header_ids)} of {len(printed_emails)} email headers"
    logger.warning(f"  -> {log_msg}, {len(fwded_articles)} of the Emails printed were forwarded articles.")
    return printed_emails


def print_json_files(epstein_files: EpsteinFiles):
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
            console.print(json_file.summary_panel)
            console.print_json(json_file.json_str(), indent=4, sort_keys=False)


def print_json_metadata(epstein_files: EpsteinFiles) -> None:
    """Print all our `DocCfg` and derived info about authorship etc."""
    json_str = epstein_files.json_metadata()

    if args.build:
        build_path = SiteType.build_path(SiteType.JSON_METADATA)

        with open(build_path, 'wt') as f:
            f.write(json_str)
            log_file_write(build_path)
    else:
        console.print_json(json_str, indent=4, sort_keys=True)


def print_other_files_section(epstein_files: EpsteinFiles) -> list[OtherFile]:
    """Returns `OtherFile` objects that were interesting enough to print."""
    if args.uninteresting:
        files = [f for f in epstein_files.other_files if not f.is_interesting]
    else:
        files = [f for f in epstein_files.other_files if args.all_other_files or f.is_interesting]

    files = Document.sort_by_timestamp(files)
    title_pfx = '' if args.all_other_files else 'Selected '
    category_table = OtherFile.summary_table(files, title_pfx=title_pfx)
    other_files_preview_table = OtherFile.files_preview_table(files, title_pfx=title_pfx)
    print_section_header(f"{FIRST_FEW_LINES} of {len(files)} {title_pfx}Files That Are Neither Emails Nor Text Messages")
    print_other_page_link(epstein_files)
    print_section_summary_table(category_table)
    console.print(other_files_preview_table)
    return files


def print_stats(epstein_files: EpsteinFiles) -> None:
    """Used to generate fixture data for pytest."""
    console.line(5)
    console.print(Panel('JSON Stats Dump', expand=True, style='reverse bold'), '\n')
    print_json(f"MessengerLog Sender Counts", MessengerLog.count_authors(epstein_files.imessage_logs), skip_falsey=True)
    print_json(f"Email Author Counts", epstein_files.email_author_counts(), skip_falsey=True)
    print_json(f"Email Recipient Counts", epstein_files.email_recipient_counts(), skip_falsey=True)
    print_json("Email signature_substitution_countss", epstein_files.email_signature_substitution_counts(), skip_falsey=True)
    print_json("email_author_device_signatures", dict_sets_to_lists(epstein_files.email_authors_to_device_signatures()))
    print_json("email_sent_from_devices", dict_sets_to_lists(epstein_files.email_device_signatures_to_authors()))
    print_json("unknown_recipient_ids", epstein_files.unknown_recipient_ids())
    print_json("count_by_month", count_by_month(epstein_files.documents))
    print_json("Interesting OtherFile IDs", sorted([f.file_id for f in epstein_files.interesting_other_files]))


def print_text_messages_section(epstein_files: EpsteinFiles) -> list[MessengerLog]:
    """Print summary table and stats for text messages. Returns objects that were printed."""
    if args.names:
        imessage_logs = [log for log in epstein_files.imessage_logs if log.author in args.names]
    else:
        imessage_logs = [log for log in epstein_files.imessage_logs if (args.all_texts or log.is_interesting)]

    if not imessage_logs:
        logger.warning(f"No MessengerLogs found for {args.names}")
        return imessage_logs

    print_section_header(('Selections from ' if not args.all_texts else '') + 'His Text Messages')
    print_centered("(conversations sorted chronologically based on timestamp of the first text message)", style='dim')

    if not args.names:
        print_section_summary_table(MessengerLog.summary_table(imessage_logs))

    for log_file in imessage_logs:
        console.print(Padding(log_file))
        console.line(2)

    return imessage_logs


def show_urls() -> None:
    """Print the various URLs generated by this code."""
    try:
        urls = {
            k: Text('[', 'grey30').append(file_size_str(SiteType.build_path(k), 1), 'cyan').append('] ').append(v, ARCHIVE_LINK_COLOR)
            for k, v in SiteType.all_urls().items()
        }
    except FileNotFoundError:
        urls = SiteType.all_urls()

    console.print(Padding(styled_dict(urls), (1)))


def write_html(output_path: Path | None) -> None:
    if not output_path:
        logger.warning(f"Not writing HTML because args.build={args.build}.")
        return

    console.save_html(str(output_path), clear=False, code_format=CONSOLE_HTML_FORMAT, theme=HTML_TERMINAL_THEME)
    log_file_write(output_path)

    if args.write_txt:
        txt_path = f"{output_path}.txt"
        console.save_text(txt_path)
        log_file_write(txt_path)


def _print_email_device_signature_info(epstein_files: EpsteinFiles) -> None:
    print_subtitle_panel(DEVICE_SIGNATURE_SUBTITLE)
    console.print(_signature_table(epstein_files.email_device_signatures_to_authors(), (DEVICE_SIGNATURE, AUTHOR), ', '))
    console.print(_signature_table(epstein_files.email_authors_to_device_signatures(), (AUTHOR, DEVICE_SIGNATURE)))


def _signature_table(keyed_sets: dict[str, set[str]], cols: tuple[str, str], join_char: str = '\n') -> Padding:
    """Build table for who signed emails with 'Sent from my iPhone' etc."""
    title = 'Email Signatures Used By Authors' if cols[0] == AUTHOR else 'Authors Seen Using Email Signatures'
    table = build_table(title, header_style="bold reverse", show_lines=True)

    for i, col in enumerate(cols):
        table.add_column(col.title() + ('s' if i == 1 else ''))

    new_dict = dict_sets_to_lists(keyed_sets)

    for k in sorted(new_dict.keys()):
        table.add_row(highlighter(k or UNKNOWN), highlighter(join_char.join(sorted(new_dict[k]))))

    return Padding(table, DEVICE_SIGNATURE_PADDING)


def _verify_all_emails_were_printed(epstein_files: EpsteinFiles, already_printed_emails: list[Email]) -> None:
    """Log warnings if some emails were never printed."""
    email_ids_that_were_printed = set([email.file_id for email in already_printed_emails])
    logger.warning(f"Printed {len(already_printed_emails):,} emails of {len(email_ids_that_were_printed):,} unique file IDs.")
    missed_an_email = False

    for email in epstein_files.unique_emails:
        if email.file_id not in email_ids_that_were_printed:
            logger.error(f"Failed to print {email.summary}")
            missed_an_email = True

    if not missed_an_email:
        logger.warning(f"All {len(epstein_files.emails):,} emails printed at least once.")
