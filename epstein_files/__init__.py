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
from rich.padding import Padding

from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import  MessengerLog
from epstein_files.epstein_files import EpsteinFiles, count_by_month
from epstein_files.util.constant.html import *
from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import EMAIL_CLASS, MESSENGER_LOG_CLASS
from epstein_files.util.data import Timer, dict_sets_to_lists
from epstein_files.util.env import args, specified_names
from epstein_files.util.file_helper import GH_PAGES_HTML_PATH, JSON_METADATA_PATH
from epstein_files.util.logging import logger
from epstein_files.util.rich import *

PRINT_COLOR_KEY_EVERY_N_EMAILS = 150

# Order matters. Default names to print emails for.
DEFAULT_EMAILERS = [
    JEREMY_RUBIN,
    AL_SECKEL,
    JOI_ITO,
    JABOR_Y,
    STEVEN_SINOFSKY,
    DANIEL_SIAD,
    JEAN_LUC_BRUNEL,
    STEVEN_HOFFENBERG,
    EHUD_BARAK,
    MARTIN_NOWAK,
    MASHA_DROKOVA,
    RENATA_BOLOTOVA,
    STEVE_BANNON,
    OLIVIER_COLOM,
    BORIS_NIKOLIC,
    PRINCE_ANDREW,
    JIDE_ZEITLIN,
    DAVID_STERN,
    MOHAMED_WAHEED_HASSAN,
    JENNIFER_JACQUET,
    None,
]

# Order matters. Default names to print tables w/email subject, timestamp, etc for.
DEFAULT_EMAILER_TABLES: list[str | None] = [
    GHISLAINE_MAXWELL,
    LEON_BLACK,
    LANDON_THOMAS,
    KATHRYN_RUEMMLER,
    DARREN_INDYKE,
    RICHARD_KAHN,
    TYLER_SHEARS,
    SULTAN_BIN_SULAYEM,
    DEEPAK_CHOPRA,
    ARIANE_DE_ROTHSCHILD,
    TOM_PRITZKER,
]

if len(set(DEFAULT_EMAILERS).intersection(set(DEFAULT_EMAILER_TABLES))) > 0:
    raise RuntimeError(f"Some names appear in both PRINT_EMAILS_FOR and PRINT_EMAILS_FOR")


def generate_html() -> None:
    timer = Timer()
    epstein_files = EpsteinFiles.get_files(timer)

    if args.json_metadata:
        metadata = [json_safe(doc.metadata()) for doc in epstein_files.all_documents()]
        json_str = json.dumps(metadata, indent=4, sort_keys=True)

        if args.build:
            with open(JSON_METADATA_PATH, 'w') as f:
                f.write(json_str)

            timer.print_at_checkpoint(f"Wrote JSON metadata to '{JSON_METADATA_PATH}' ({file_size_str(JSON_METADATA_PATH)})")
        else:
            console.print_json(json_str)

        exit()

    print_header(epstein_files)

    if args.colors_only:
        exit()

    if args.output_texts:
        _print_text_messages(epstein_files)
        timer.print_at_checkpoint(f'Printed {len(epstein_files.imessage_logs)} text message logs')

    if args.output_emails:
        emails_printed = _print_emails(epstein_files)
        timer.print_at_checkpoint(f"Printed {emails_printed:,} emails")

    if args.output_other_files:
        files_printed = epstein_files.print_other_files_table()
        timer.print_at_checkpoint(f"Printed {len(files_printed)} other files")

    # Save output
    write_html(GH_PAGES_HTML_PATH)
    logger.warning(f"Total time: {timer.seconds_since_start_str()}")

    # JSON stats (mostly used for building pytest checks)
    if args.json_stats:
        console.line(5)
        _print_json_stats(epstein_files)


def _print_emails(epstein_files: EpsteinFiles) -> int:
    """Returns number of emails printed."""
    print_section_header(('Selections from ' if not args.all_emails else '') + 'His Emails')
    print_other_site_link(is_header=False)

    if len(specified_names) == 0:
        epstein_files.print_emailer_counts_table()

    emailers_to_print: list[str | None]
    emailer_tables: list[str | None] = []
    already_printed_emails: list[Email] = []
    num_emails_printed_since_last_color_key = 0

    if args.all_emails:
        console.print('Email conversations are sorted chronologically based on time of the first email.')
        emailers_to_print = sorted(epstein_files.all_emailers(), key=lambda e: epstein_files.earliest_email_at(e))
        print_numbered_list_of_emailers(emailers_to_print, epstein_files)
    else:
        emailers_to_print = specified_names if specified_names else DEFAULT_EMAILERS
        console.print('Email conversations grouped by counterparty can be found in the order listed below.')
        print_numbered_list_of_emailers(emailers_to_print)
        console.print("\nAfter that there's tables linking to (but not displaying) all known emails for each of these people:")

        if len(specified_names) > 0:
            print_numbered_list_of_emailers(DEFAULT_EMAILER_TABLES)

    for author in emailers_to_print:
        newly_printed_emails = epstein_files.print_emails_for(author)
        already_printed_emails.extend(newly_printed_emails)
        num_emails_printed_since_last_color_key += len(newly_printed_emails)

        # Print color key every once in a while
        if num_emails_printed_since_last_color_key > PRINT_COLOR_KEY_EVERY_N_EMAILS:
            print_color_key()
            num_emails_printed_since_last_color_key = 0

    if not specified_names:
        if not args.all_emails:
            print_author_header(f"Email Tables for {len(emailer_tables)} Other People", 'white')

            for name in DEFAULT_EMAILER_TABLES:
                epstein_files.print_emails_table_for(name)

        epstein_files.print_email_device_info()

    # Check that all emails were actually printed
    if args.all_emails:
        email_ids_that_were_printed = set([email.file_id for email in already_printed_emails])
        logger.warning(f"Printed {len(already_printed_emails)} emails of {len(email_ids_that_were_printed)} unique file IDs.")

        for email in epstein_files.emails:
            if email.file_id not in email_ids_that_were_printed and not email.is_duplicate:
                logger.warning(f"Failed to print {email.summary()}")

    logger.warning(f"Rewrote {len(Email.rewritten_header_ids)} headers of {len(epstein_files.emails)} emails")
    return len(already_printed_emails)


def _print_text_messages(epstein_files: EpsteinFiles) -> None:
    print_section_header('Text Messages')
    print_centered("(conversations are sorted chronologically based on timestamp of first message)\n", style='gray30')
    authors: list[str | None] = specified_names if specified_names else [JEFFREY_EPSTEIN]
    log_files = epstein_files.imessage_logs_for(authors)

    for log_file in log_files:
        console.print(Padding(log_file))
        console.line(2)

    epstein_files.print_imessage_summary()


def _print_json_stats(epstein_files: EpsteinFiles) -> None:
    console.print(Panel('JSON Stats Dump', expand=True, style='reverse bold'), '\n')
    print_json(f"{MESSENGER_LOG_CLASS} Sender Counts", MessengerLog.count_authors(epstein_files.imessage_logs), skip_falsey=True)
    print_json(f"{EMAIL_CLASS} Author Counts", epstein_files.email_author_counts, skip_falsey=True)
    print_json(f"{EMAIL_CLASS} Recipient Counts", epstein_files.email_recipient_counts, skip_falsey=True)
    print_json("Email signature_substitution_countss", epstein_files.email_signature_substitution_counts(), skip_falsey=True)
    print_json("email_author_device_signatures", dict_sets_to_lists(epstein_files.email_authors_to_device_signatures))
    print_json("email_sent_from_devices", dict_sets_to_lists(epstein_files.email_device_signatures_to_authors))
    print_json("email_unknown_recipient_file_ids", epstein_files.email_unknown_recipient_file_ids())
    print_json("count_by_month", count_by_month(epstein_files.all_documents()))
