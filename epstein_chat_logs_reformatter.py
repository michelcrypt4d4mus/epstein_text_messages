#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_

Install: 'pip install python-dotenv rich'
    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT/001 ./epstein_chat_logs_reformatter.py'
"""
import re
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
load_dotenv()

from documents.epstein_files import EpsteinFiles
from documents.messenger_log import MSG_REGEX
from util.env import deep_debug, is_debug
from util.rich import *

OUTPUT_DIR = Path('docs')
OUTPUT_GH_PAGES_HTML = OUTPUT_DIR.joinpath('index.html')
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')

TEXTER_MAPPING = {
    'e:jeeitunes@gmail.com': EPSTEIN,
    '+19174393646': SCARAMUCCI,
    '+13109906526': BANNON,
}

UNKNOWN_TEXTERS = [
    '+16463880059',
    '+13108737937',
    '+13108802851',
    'e:',
    '+',
    None,
]

sender_counts = defaultdict(int)
convos_labeled = 0
msgs_processed = 0
print_header()
epstein_files = EpsteinFiles()

for log_file in epstein_files.sorted_imessage_logs():
    console.print(Panel(archive_link(log_file.filename, log_file.author_style), expand=False))

    if log_file.hint_txt:
        console.print(log_file.hint_txt)

    console.line()

    for match in MSG_REGEX.finditer(log_file.text):
        sender = sender_str = match.group(1).strip()
        timestamp = Text(f"[{match.group(2).strip()}] ", style='gray30')
        msg = match.group(4).strip()
        msg_lines = msg.split('\n')
        sender_style = None
        sender_txt = None

        # If the Sender: is redacted we need to fill it in from our configuration
        if len(sender) == 0:
            sender = log_file.author
            sender_str = log_file.author_str
            sender_txt = log_file.author_txt
        else:
            if sender in TEXTER_MAPPING:
                sender = sender_str = TEXTER_MAPPING[sender]
            elif PHONE_NUMBER_REGEX.match(sender):
                sender_style = PHONE_NUMBER
            elif re.match('[ME]+', sender):
                sender = MELANIE_WALKER

            sender_txt = Text(sender_str, style=sender_style or COUNTERPARTY_COLORS.get(sender, DEFAULT))

        # Fix multiline links
        if msg.startswith('http'):
            if len(msg_lines) > 1 and not msg_lines[0].endswith('html'):
                if len(msg_lines) > 2 and msg_lines[1].endswith('-'):
                    msg = msg.replace('\n', '', 2)
                else:
                    msg = msg.replace('\n', '', 1)

            msg_lines = msg.split('\n')
            link_text = msg_lines.pop()
            msg = Text('').append(link_text, style=TEXT_LINK)

            if len(msg_lines) > 0:
                msg = msg.append('\n' + ' '.join(msg_lines))
        else:
            msg = msg.replace('\n', ' ')  # remove newlines

        sender_counts[UNKNOWN if (sender in UNKNOWN_TEXTERS or re.match(r'^([-+_1•F]+|[4Ide])$', sender)) else sender] += 1
        console.print(Text('').append(timestamp).append(sender_txt).append(': ', style='dim').append(msg))
        msgs_processed += 1

    if log_file.author != UNKNOWN:
        convos_labeled += 1

    console.line(2)


# Text message counts
counts_table = Table(title="Text Message Counts By Author", show_header=True, header_style="bold")
counts_table.add_column("Sender", style="steel_blue bold", justify="left", width=30)
counts_table.add_column("Message Count", justify="center")

for k, v in sorted(sender_counts.items(), key=lambda item: item[1], reverse=True):
    counts_table.add_row(Text(k, COUNTERPARTY_COLORS.get(k, 'grey23 bold')), str(v))

console.print(counts_table)
console.print(f"\nFound {msgs_processed} text messages in {len(epstein_files.iMessage_logs)} iMessage logs of {len(epstein_files.all_files)} total files ({convos_labeled} files deanonymized).")
console.print(f"(Last deploy found 77 files with 4668 messages)\n", style='dim')


# Email sender / recipient counts
console.line(2)
console.print(Panel(Text("HIS EMAILS", justify='center', style='bold'), expand=True, padding=(2, 2)), style='bold on blue3')


def print_email_table(counts: dict[str, int], column_title: str) -> None:
    counts_table = Table(title=f"Email Counts By {column_title}", show_header=True, header_style="bold")
    counts_table.add_column(column_title, justify="left")
    counts_table.add_column("Email Count", justify="center")

    for k, v in sorted(counts.items(), key=lambda item: [item[1], item[0]], reverse=True):
        k = k.title() if ' ' in k else k
        counts_table.add_row(f"[steel_blue][link={epsteinify_url(k)}]{k}[/link][/steel_blue]", str(v))

    console.print('\n', counts_table)


print_email_table(epstein_files.email_author_counts, "Author")
print_email_table(epstein_files.email_recipient_counts, "Recipients")

console.print(f"\n\nScanned {len(epstein_files.emails)} potential emails, found {sum([i for i in epstein_files.email_author_counts.values()])} senders.")
console.print('Chronologically sorted emails Epstein sent to or received from these people can be found below:\n')

for i, author in enumerate(PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED):
    style = COUNTERPARTY_COLORS.get(author or UNKNOWN, DEFAULT)
    console.print(Text(f"   {i}. ", style='bold').append(author or UNKNOWN, style=style))

# Emails
for author in PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED:
    epstein_files.print_emails_for(author)


if not is_debug:
    console.save_html(OUTPUT_GH_PAGES_HTML, inline_styles=False, clear=False, code_format=CONSOLE_HTML_FORMAT)
    console.print(f"\nWrote HTML to '{OUTPUT_GH_PAGES_HTML}'.")
else:
    console.print(f"\nNot writing HTML because DEBUG=true.")
