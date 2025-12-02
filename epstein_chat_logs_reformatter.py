#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_

Install: 'pip install python-dotenv rich'
    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT/001 ./epstein_chat_logs_reformatter.py'
"""
import time
from pathlib import Path
from sys import exit

from dotenv import load_dotenv
load_dotenv()
from rich.padding import Padding
from rich.text import Text

from documents.epstein_files import EpsteinFiles
from util.env import specified_emailers, args, is_build, is_debug, skip_texts
from util.file_helper import OUTPUT_GH_PAGES_HTML
from util.html import *
from util.rich import *

PRINT_COLOR_KEY_EVERY_N_EMAILS = 150

# Order matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED_LIST = [
    JEREMY_RUBIN,
    JOI_ITO,
    AL_SECKEL,
    JABOR_Y,
    DANIEL_SIAD,
    JEAN_LUC_BRUNEL,
    EHUD_BARAK,
    MARTIN_NOWAK,
    MASHA_DROKOVA,
    STEVE_BANNON,
    ARIANE_DE_ROTHSCHILD,
    OLIVIER_COLOM,
    BORIS_NIKOLIC,
    PRINCE_ANDREW,
    TOM_PRITZKER,
    JIDE_ZEITLIN,
    DAVID_STERN,
    MOHAMED_WAHEED_HASSAN,
    None,
]

# Order matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES_LIST = [
    GHISLAINE_MAXWELL,
    LEON_BLACK,
    LANDON_THOMAS,
    KATHY_RUEMMLER,
    DARREN_INDYKE,
    RICHARD_KAHN,
    TYLER_SHEARS,
    SULTAN_BIN_SULAYEM,
    DEEPAK_CHOPRA,
]


started_at = time.perf_counter()
emails_printed = 0
print_header()

if args.colors_only:
    print_color_key()
    exit()

epstein_files = EpsteinFiles()
finished_processing_at = checkpoint_at = time.perf_counter()
epstein_files.print_files_overview()
print_color_key()


# Text messages section
if not skip_texts:
    print_section_header('Text Messages')
    print_centered("(conversations are sorted chronologically based on timestamp of first message)\n", style='gray30')

    for log_file in epstein_files.imessage_logs:
        console.print(Padding(log_file))
        console.line(2)

    epstein_files.print_imessage_summary()
    logger.warning(f"Printed texts in {(time.perf_counter() - checkpoint_at):.2f} seconds")
    checkpoint_at = time.perf_counter()


# Emails section
print_section_header(('Selections from ' if not args.all_emails else '') + 'His Emails')
print_other_site_link(is_header=False)
epstein_files.print_emailer_counts_table()

if args.all_emails:
    console.print('Email conversations are sorted chronologically based on time of the first email.')
    emailers_to_print = sorted(epstein_files.all_emailers(), key=lambda e: epstein_files.earliest_email_at(e))
    print_numbered_list_of_emailers(emailers_to_print, epstein_files)
else:
    if len(specified_emailers) > 0:
        PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED_LIST = specified_emailers

    console.print('Email conversations grouped by counterparty can be found in the order listed below.')
    emailers_to_print = PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED_LIST
    print_numbered_list_of_emailers(emailers_to_print)
    console.print("\nAfter that there's tables linking to (but not displaying) all known emails for each of these people:")

    if args.all_email_tables:
        emailer_tables = sorted(epstein_files.all_emailers(), key=lambda e: epstein_files.earliest_email_at(e))
    else:
        emailer_tables = PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES_LIST

    print_numbered_list_of_emailers(emailer_tables)

for author in emailers_to_print:
    emails_printed += epstein_files.print_emails_for(author)

    if emails_printed > PRINT_COLOR_KEY_EVERY_N_EMAILS:
        print_color_key()
        emails_printed = 0

if not args.all_emails and len(specified_emailers) == 0:
    print_author_header(f"Email Tables for {len(emailer_tables)} Other People", 'white')

    for name in emailer_tables:
        epstein_files.print_emails_table_for(name)

epstein_files.print_email_device_info()
logger.warning(f"Printed {len(epstein_files.emails)} emails in {(time.perf_counter() - checkpoint_at):.2f} seconds")
checkpoint_at = time.perf_counter()


# Other Files Section
if not skip_texts:
    print_section_header(f"Top Lines of {len(epstein_files.other_files)} Files That Are Neither Emails Nor Text Msgs")
    epstein_files.print_other_files_table()
    logger.warning(f"Printed other files in {(time.perf_counter() - checkpoint_at):.2f} seconds")
    checkpoint_at = time.perf_counter()
else:
    logger.warning(f"Skipping other files section (is_build={is_build}, args.all_emails={args.all_emails}, skip_texts={skip_texts})...")


# Save output
if is_build:
    console.save_html(OUTPUT_GH_PAGES_HTML, code_format=CONSOLE_HTML_FORMAT, inline_styles=False, theme=HTML_TERMINAL_THEME)
    html_size_in_mb = round(OUTPUT_GH_PAGES_HTML.stat().st_size / 1024 / 1024, 2)
    logger.warning(f"Wrote HTML to '{OUTPUT_GH_PAGES_HTML}' ({html_size_in_mb} MB, total time {(time.perf_counter() - started_at):.2f} seconds).\n")
else:
    logger.warning(f"Not writing HTML because 'BUILD_HTML' env var not set, total time {(time.perf_counter() - started_at):.2f} seconds.")
