#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_

Install: 'pip install python-dotenv rich'
    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT/001 ./epstein_chat_logs_reformatter.py'
"""
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from documents.epstein_files import EpsteinFiles
from documents.messenger_log import sender_counts
from util.env import is_build, is_debug
from util.rich import *

OUTPUT_GH_PAGES_HTML = Path('docs').joinpath('index.html')


print_header()
epstein_files = EpsteinFiles()

# Text messages
for log_file in epstein_files.sorted_imessage_logs():
    console.print(log_file)
    console.line(2)

counts_table = Table(title="Text Message Counts By Author", show_header=True, header_style="bold")
counts_table.add_column("Sender", style="steel_blue bold", justify="left", width=30)
counts_table.add_column("Message Count", justify="center")

for k, v in sorted(sender_counts.items(), key=lambda item: item[1], reverse=True):
    counts_table.add_row(Text(k, COUNTERPARTY_COLORS.get(k, 'grey23 bold')), str(v))

console.print(counts_table)
text_summary_msg = f"\nDeanonymized {epstein_files.identified_imessage_log_count()} of "
text_summary_msg += f"{len(epstein_files.iMessage_logs)} text msg logs found in {len(epstein_files.all_files)} files."
console.print(text_summary_msg)
console.print(f"Found {epstein_files.imessage_msg_count()} total text messages in {len(epstein_files.iMessage_logs)} conversations.")
console.print(f"(Last deploy found 4668 messages in 77 conversations)\n\n\n", style='dim')

# Email sender / recipient counts
console.print(Panel(Text("HIS EMAILS", justify='center'), width=80, padding=(2, 2)), style='bold white on blue3')
print_email_table(epstein_files.email_author_counts, "Author")
print_email_table(epstein_files.email_recipient_counts, "Recipients")
console.print(f"\n\nIdentified {epstein_files.num_identified_email_authors()} authors in {len(epstein_files.emails)} potential email files.")
console.print('Chronological Epstein correspondence with the following people can be found below.')
console.print('(note this site uses the OCR email text provided by Congress which is not the greatest)\n', style='dim')

for i, author in enumerate(PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED):
    style = COUNTERPARTY_COLORS.get(author or UNKNOWN, DEFAULT)
    console.print(Text(f"   {i}. ", style='bold').append(author or UNKNOWN, style=style))

console.print("\n\nAfter that there's tables linking to (but not displaying) all known emails for each of these folks:\n")

for i, author in enumerate(PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES):
    style = COUNTERPARTY_COLORS.get(author or UNKNOWN, DEFAULT)
    console.print(Text(f"   {i}. ", style='bold').append(author or UNKNOWN, style=style))

for author in PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED:
    epstein_files.print_emails_for(author)

# Print everyone with less than 3 sent emails
# low_sent = [a for a in epstein_files.email_author_counts.keys() if len(epstein_files.emails_for(a)) < 3]
# for author in [a for a in epstein_files.email_recipient_counts.keys() if len(epstein_files.emails_for(a)) < 3 and a not in low_sent]:
#     epstein_files.print_emails_for(author)

for name in PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES.keys():
    epstein_files.print_emails_table_for(name)

# Save output
if is_build:
    console.save_html(OUTPUT_GH_PAGES_HTML, inline_styles=False, clear=False, code_format=CONSOLE_HTML_FORMAT)
    console.print(f"\nWrote HTML to '{OUTPUT_GH_PAGES_HTML}'.")
else:
    console.print(f"\nNot writing HTML, BUILD_HTML not set.")
