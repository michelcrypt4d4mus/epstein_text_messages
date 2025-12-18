#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_

Install: 'poetry install'
    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT/001 ./generate.py'
"""
from sys import exit

from dotenv import load_dotenv
load_dotenv()
from rich.padding import Padding

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.constant.html import *
from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import EMAIL_CLASS, MESSENGER_LOG_CLASS
from epstein_files.util.data import Timer, dict_sets_to_lists, flatten
from epstein_files.util.env import specified_names, args
from epstein_files.util.file_helper import GH_PAGES_HTML_PATH
from epstein_files.util.rich import *

PRINT_COLOR_KEY_EVERY_N_EMAILS = 150

# Order matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED: list[str | None] = [
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
    None,
]

# Order matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES: list[str | None] = [
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


def generate_html() -> None:
    timer = Timer()
    epstein_files = EpsteinFiles.get_files(timer)
    print_header(epstein_files)

    if args.colors_only:
        exit()

    # Text messages section
    if args.output_texts:
        print_text_messages(epstein_files)
        timer.print_at_checkpoint(f'Printed {len(epstein_files.imessage_logs):,} text message logs')

    # Emails section
    if args.output_emails:
        emails_printed = print_emails(epstein_files)
        timer.print_at_checkpoint(f"Printed {emails_printed:,} emails")

    if args.output_other_files:
        print_section_header(f"Top Lines of {len(epstein_files.other_files)} Files That Are Neither Emails Nor Text Msgs")
        epstein_files.print_other_files_table()
        timer.print_at_checkpoint(f"Printed {len(epstein_files.other_files):,} other files")
    else:
        logger.warning(f"Skipping other files section...")

    # Save output
    write_html(GH_PAGES_HTML_PATH)
    logger.warning(f"Total time: {timer.seconds_since_start()}")

    # JSON stats
    if args.json_stats:
        console.line(5)
        print_json_stats(epstein_files)


def print_emails(epstein_files: EpsteinFiles) -> int:
    """Returns number of emails printed."""
    print_section_header(('Selections from ' if not args.all_emails else '') + 'His Emails')
    print_other_site_link(is_header=False)
    epstein_files.print_emailer_counts_table()
    emailers_to_print: list[str | None]
    emailer_tables: list[str | None] = []
    emails_printed_since_last_color_key = 0
    emails_printed_total = 0

    if args.all_emails:
        console.print('Email conversations are sorted chronologically based on time of the first email.')
        emailers_to_print = sorted(epstein_files.all_emailers(), key=lambda e: epstein_files.earliest_email_at(e))
        print_numbered_list_of_emailers(emailers_to_print, epstein_files)
    else:
        if len(specified_names) > 0:
            emailers_to_print = specified_names
        else:
            emailers_to_print = PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED

        console.print('Email conversations grouped by counterparty can be found in the order listed below.')
        print_numbered_list_of_emailers(emailers_to_print)
        console.print("\nAfter that there's tables linking to (but not displaying) all known emails for each of these people:")

        if args.all_email_tables:
            emailer_tables = sorted(epstein_files.all_emailers(), key=lambda e: epstein_files.earliest_email_at(e))
        else:
            emailer_tables = PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES

        print_numbered_list_of_emailers(emailer_tables)

    for author in emailers_to_print:
        emails_printed = epstein_files.print_emails_for(author)
        emails_printed_total += emails_printed
        emails_printed_since_last_color_key += emails_printed

        # Print color key every once in a while
        if emails_printed_since_last_color_key > PRINT_COLOR_KEY_EVERY_N_EMAILS:
            print_color_key()
            emails_printed_since_last_color_key = 0

    if len(emailer_tables) > 0:
        print_author_header(f"Email Tables for {len(emailer_tables)} Other People", 'white')

        for name in emailer_tables:
            epstein_files.print_emails_table_for(name)

    epstein_files.print_email_device_info()
    return emails_printed_total


def print_text_messages(epstein_files: EpsteinFiles) -> None:
    print_section_header('Text Messages')
    print_centered("(conversations are sorted chronologically based on timestamp of first message)\n", style='gray30')

    if len(specified_names) == 0:
        log_files = epstein_files.imessage_logs
    else:
        log_files = flatten([epstein_files.imessage_logs_for(name) for name in specified_names])

    for log_file in log_files:
        console.print(Padding(log_file))
        console.line(2)

    epstein_files.print_imessage_summary()


def print_json_stats(epstein_files: EpsteinFiles) -> None:
    console.print(Panel('JSON Stats Dump', expand=True, style='reverse bold'), '\n')
    print_json(f"{MESSENGER_LOG_CLASS} Sender Counts", epstein_files.imessage_sender_counts(), skip_falsey=True)
    print_json(f"{EMAIL_CLASS} Author Counts", epstein_files.email_author_counts, skip_falsey=True)
    print_json(f"{EMAIL_CLASS} Recipient Counts", epstein_files.email_recipient_counts, skip_falsey=True)
    print_json("Email signature_substitution_counts", epstein_files.email_signature_substitution_counts(), skip_falsey=True)
    print_json("email_author_device_signatures", dict_sets_to_lists(epstein_files.email_authors_to_device_signatures))
    print_json("email_sent_from_devices", dict_sets_to_lists(epstein_files.email_device_signatures_to_authors))
    print_json("email_unknown_recipient_file_ids", epstein_files.email_unknown_recipient_file_ids())
