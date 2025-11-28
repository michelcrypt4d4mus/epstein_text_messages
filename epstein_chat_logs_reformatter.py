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
from rich.table import Table
from rich.text import Text

from documents.email_header import AUTHOR
from documents.epstein_files import EpsteinFiles
from documents.messenger_log import sender_counts
from util.env import args, is_build, is_debug, skip_texts
from util.file_helper import OUTPUT_GH_PAGES_HTML
from util.rich import *
from util.html import *


print_header()
epstein_files = EpsteinFiles()
epstein_files.print_summary()


# Text messages section
if not skip_texts:
    print_section_header('Text Messages')

    for log_file in epstein_files.imessage_logs:
        console.print(log_file)
        console.line(2)

    counts_table = Table(title="Text Message Counts By Author", show_header=True, header_style="bold")
    counts_table.add_column(AUTHOR.title(), style="steel_blue bold", justify="left", width=30)
    counts_table.add_column("Message Count", justify="center")

    for k, v in sorted(sender_counts.items(), key=lambda item: item[1], reverse=True):
        counts_table.add_row(Text(k, COUNTERPARTY_COLORS.get(k, 'grey23 bold')), str(v))

    console.print(counts_table)
    text_summary_msg = f"\nDeanonymized {epstein_files.identified_imessage_log_count()} of "
    text_summary_msg += f"{len(epstein_files.imessage_logs)} text msg logs found in {len(epstein_files.all_files)} files."
    console.print(text_summary_msg)
    console.print(f"Found {epstein_files.imessage_msg_count()} total text messages in {len(epstein_files.imessage_logs)} conversations.")
    console.print(f"(Last deploy found 4668 messages in 77 conversations)\n\n\n", style='dim')


# Emails section
print_section_header('His Emails')
print_all_emails_link()
console.line()
print_emailer_counts_table(epstein_files.email_author_counts, AUTHOR.title())
console.line(2)
print_emailer_counts_table(epstein_files.email_recipient_counts, "Recipient")
console.print(f"\n\nIdentified authors of {epstein_files.num_identified_email_authors()} emails out of {len(epstein_files.emails)} potential email files.")
console.print('(note this site is based on the OCR email text provided by Congress which is not the greatest)\n', style='dim')
console.print('Epstein correspondence grouped by counterparty can be found below. Groups are sorted chronologically based on time of the first email.')

emailers_to_print = epstein_files.all_emailers() if args.all else PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED
emailers_to_print = sorted(emailers_to_print, key=lambda e: epstein_files.earliest_email_at(e)) if args.all else emailers_to_print
print_numbered_list(emailers_to_print)

if not args.all:
    console.print("\n\nAfter that there's tables linking to (but not displaying) all known emails for each of these people:\n")
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
    console.line()
    print_section_header(f"The {len(epstein_files.other_files)} Files That Are Neither Emails Nor Text Msgs")
    epstein_files.print_other_files_table()
else:
    print(f"Skipping other files section (is_build={is_build}, args.all={args.all})...")


# Save output
if is_build:
    console.save_html(OUTPUT_GH_PAGES_HTML, code_format=CONSOLE_HTML_FORMAT, inline_styles=False, theme=HTML_TERMINAL_THEME)
    console.print(f"\nWrote HTML to '{OUTPUT_GH_PAGES_HTML}', not computing signatures.")
else:
    console.print(f"\nNot writing HTML because 'BUILD_HTML' env var not set.")
