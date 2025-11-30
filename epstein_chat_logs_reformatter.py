#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_

Install: 'pip install python-dotenv rich'
    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT/001 ./epstein_chat_logs_reformatter.py'
"""
from pathlib import Path
from sys import exit

from dotenv import load_dotenv
load_dotenv()
from rich.columns import Columns
from rich.console import Console
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from documents.email_header import AUTHOR
from documents.epstein_files import EpsteinFiles
from documents.messenger_log import sender_counts
from util import rich
from util.env import additional_emailers, args, is_build, is_debug, skip_texts
from util.file_helper import OUTPUT_GH_PAGES_HTML
from util.rich import *
from util.html import *

COLOR_KEYS = [
    Text(color_name.removesuffix(COLOR_SUFFIX).lower(), style=getattr(rich, color_name))
    for color_name in sorted([constant for constant in dir(rich) if constant.endswith(COLOR_SUFFIX)])
    if color_name not in ['ARCHIVE_LINK_COLOR', 'DUBIN_COLOR', 'DEFAULT_NAME_COLOR']
]


print_header()
print_color_key(COLOR_KEYS)

if args.colors_only:
    exit()

epstein_files = EpsteinFiles()
epstein_files.print_summary()


# Text messages section
if not skip_texts:
    print_section_header('Text Messages')
    print_centered("(conversations are sorted chronologically based on timestamp of first message)\n", style='gray30')

    for log_file in epstein_files.imessage_logs:
        console.print(Padding(log_file))
        console.line(2)

    epstein_files.print_imessage_summary()


# Emails section
print_section_header(('Selections from ' if not args.all else '') + 'His Emails')
print_other_site_link(is_header=False)
epstein_files.print_emailer_counts_table()

if args.all:
    console.print('Email conversations are sorted chronologically based on time of the first email.', style='dim')
    emailers_to_print = sorted(epstein_files.all_emailers(), key=lambda e: epstein_files.earliest_email_at(e))
    print_numbered_list(emailers_to_print, epstein_files)
else:
    if len(additional_emailers) > 0:
        PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED.update({k: get_style_for_name(k) for k in additional_emailers})

    console.print('Email conversations grouped by counterparty can be found in the order listed below.')
    emailers_to_print = [e for e in PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED.keys()]
    print_numbered_list(emailers_to_print)
    console.print("\nAfter that there's tables linking to (but not displaying) all known emails for each of these people:")
    emailer_tables = epstein_files.all_emailers() if args.all_tables else PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES
    emailer_tables = sorted(emailer_tables, key=lambda e: epstein_files.earliest_email_at(e)) if args.all_tables else emailer_tables
    print_numbered_list(emailer_tables)

for author in emailers_to_print:
    epstein_files.print_emails_for(author)

if not args.all:
    print_author_header(f"Email Tables for {len(emailer_tables)} Other People", 'white')

    for name in emailer_tables:
        epstein_files.print_emails_table_for(name)

epstein_files.print_email_device_info()


# Other Files Section
if is_build and not args.all:
    print_section_header(f"Top Lines of {len(epstein_files.other_files)} Files That Are Neither Emails Nor Text Msgs")
    epstein_files.print_other_files_table()
else:
    logger.warning(f"Skipping other files section (is_build={is_build}, args.all={args.all})...")


# Save output
if is_build:
    console.save_html(OUTPUT_GH_PAGES_HTML, code_format=CONSOLE_HTML_FORMAT, inline_styles=False, theme=HTML_TERMINAL_THEME)
    html_size_in_mb = round(OUTPUT_GH_PAGES_HTML.stat().st_size / 1024 / 1024, 2)
    logger.warning(f"Wrote HTML to '{OUTPUT_GH_PAGES_HTML}' ({html_size_in_mb} MB).")
else:
    logger.warning(f"Not writing HTML because 'BUILD_HTML' env var not set.")
