#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_

Install: 'pip install rich'
    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT/archive ./epstein_chat_logs_reformatter.py'
"""
import re
import urllib.parse
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
load_dotenv()

from util.emails import DETECT_EMAIL_REGEX, KNOWN_EMAILS, extract_email_sender, cleanup_email_txt
from util.env import deep_debug, include_redacted_emails, is_debug
from util.file_helper import MSG_REGEX, extract_file_id, first_timestamp_in_file, get_files_in_dir, load_file, move_json_file
from util.rich import *

OUTPUT_DIR = Path('docs')
OUTPUT_GH_PAGES_HTML = OUTPUT_DIR.joinpath('index.html')
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')
TOTAL = 'TOTAL'

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
]

search_archive_url = lambda txt: f"{COURIER_NEWSROOM_ARCHIVE}&page=1&q={urllib.parse.quote(txt)}&p=1"
archive_link = lambda file: f"[bold][{ARCHIVE_LINK_COLOR}][link={search_archive_url(file)}]{file}[/link][/{ARCHIVE_LINK_COLOR}][/bold]"
sender_counts = defaultdict(int)
emailer_counts = defaultdict(int)
redacted_emails = {}
convos_labeled = 0
files_found = 0
files_processed = 0
msgs_processed = 0


def get_imessage_log_files(files: list[Path]) -> list[Path]:
    """Scan text files, count email senders, and return filtered list of iMessage log file paths."""
    log_files = []

    for file_arg in files:
        if deep_debug:
            console.print(f"\nScanning '{file_arg.name}'...", style='dim')

        file_text = load_file(file_arg)
        file_lines = file_text.split('\n')
        file_id = extract_file_id(file_arg.name)

        if len(file_text) == 0:
            if is_debug:
                console.print(f"   -> Skipping empty file...", style='dim')

            continue
        elif file_text[0] == '{':  # Check for JSON
            move_json_file(file_arg)
        elif MSG_REGEX.search(file_text):
            log_files.append(file_arg)
        else:
            emailer = None

            if DETECT_EMAIL_REGEX.match(file_text):  # Handle emails
                emailer_counts[TOTAL] += 1

                try:
                    emailer = KNOWN_EMAILS.get(file_id) or extract_email_sender(file_text) or UNKNOWN
                    emailer_counts[emailer.lower()] += 1

                    if deep_debug:
                        console.print(f"   -> Emailer: '{emailer}'", style='dim')

                    if len(emailer) >= 3 and emailer != UNKNOWN:
                        continue  # Don't proceed to printing debug contents if we found a valid email
                    elif len(emailer) >= 3:
                        redacted_emails[file_arg.name] = file_text
                except Exception as e:
                    console.print_exception()
                    console.print(f"\nError file '{file_arg.name}' with {len(file_lines)} lines, top lines:")
                    print_top_lines(file_text)
                    raise e

            if is_debug:
                console.print(f"Unknown kind of file '{file_arg.name}' with {len(file_lines)} lines. First lines:")

                if emailer and emailer != UNKNOWN:
                    console.print(f"Failed to find valid email (got '{emailer}')", style='red')

                print_top_lines(file_text)

            continue

    return sorted(log_files, key=lambda f: first_timestamp_in_file(f))   # Sort by first timestamp


print_header()
files = get_files_in_dir()

for file_arg in get_imessage_log_files(files):
    files_processed += 1
    file_text = load_file(file_arg)
    file_lines = file_text.split('\n')
    file_id = extract_file_id(file_arg.name)
    console.print(Panel(archive_link(file_arg.name), expand=False))
    counterparty = KNOWN_COUNTERPARTY_FILE_IDS.get(file_id, UNKNOWN)
    counterparty_guess = None

    if counterparty != UNKNOWN:
        hint_txt = Text(f"Found confirmed counterparty ", style='grey')
        hint_txt.append(counterparty, style=COUNTERPARTY_COLORS.get(counterparty, DEFAULT))
        console.print(hint_txt.append(f" for file ID {file_id}."))
        convos_labeled += 1
    elif file_id in GUESSED_COUNTERPARTY_FILE_IDS:
        counterparty_guess = GUESSED_COUNTERPARTY_FILE_IDS[file_id]
        txt = Text("(This is probably a conversation with ", style='grey')
        txt.append(counterparty_guess, style=f"{COUNTERPARTY_COLORS.get(counterparty_guess, DEFAULT)}")
        console.print(txt.append(')'), style='dim')
        convos_labeled += 1

    console.line()

    for match in MSG_REGEX.finditer(file_text):
        sender = sender_str = match.group(1).strip()
        timestamp = Text(f"[{match.group(2).strip()}] ", style='gray30')
        msg = match.group(4).strip()
        msg_lines = msg.split('\n')
        sender_style = None

        # If the Sender: is redacted we need to fill it in from our configuration
        if len(sender) == 0:
            if counterparty != UNKNOWN:
                sender = sender_str = counterparty
            elif counterparty_guess is not None:
                sender = counterparty_guess
                sender_str = f"{counterparty_guess} (?)"
            else:
                sender = sender_str = UNKNOWN
        else:
            if sender in TEXTER_MAPPING:
                sender = sender_str = TEXTER_MAPPING[sender]
            elif PHONE_NUMBER_REGEX.match(sender):
                sender_style = PHONE_NUMBER
            elif re.match('[ME]+', sender):
                sender = MELANIE_WALKER

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

        sender_counts[UNKNOWN if (re.match(r'^([-+_1•F]+|[4Ide])$', sender) or sender in UNKNOWN_TEXTERS) else sender] += 1
        sender_txt = Text(sender_str, style=sender_style or COUNTERPARTY_COLORS.get(sender, DEFAULT))
        console.print(Text('').append(timestamp).append(sender_txt).append(': ', style='dim').append(msg))
        msgs_processed += 1

    console.line(2)


# Text message counts
counts_table = Table(title="Message Counts By Sender", show_header=True, header_style="bold")
counts_table.add_column("Sender", style="steel_blue bold", justify="left", width=30)
counts_table.add_column("Message Count", justify="center")

for k, v in sorted(sender_counts.items(), key=lambda item: item[1], reverse=True):
    counts_table.add_row(Text(k, COUNTERPARTY_COLORS.get(k, 'grey23 bold')), str(v))

console.print(counts_table)
console.print(f"\nFound {msgs_processed} text messages in {files_processed} iMessage logs of {len(files)} total files ({convos_labeled} files deanonymized).")
console.print(f"(Last deploy found 77 files with 4668 messages)\n", style='dim')


# Email sender counts
console.line(2)
console.print(Panel(Text("Email Analysis", justify='center', style='bold'), expand=True), style='bold reverse')
console.line()
num_potential_emails = emailer_counts.pop(TOTAL)
counts_table = Table(title="Email Counts By Sender", show_header=True, header_style="bold")
counts_table.add_column("From", justify="left")
counts_table.add_column("Email Count", justify="center")

for k, v in sorted(emailer_counts.items(), key=lambda item: item[1], reverse=True):
    counts_table.add_row(f"[steel_blue][link={search_archive_url(k)}]{k}[/link][/steel_blue]", str(v))

console.print(counts_table)
console.print(f"\nScanned {num_potential_emails} potential emails, found {sum([i for i in emailer_counts.values()])} senders.")

# Redacted emails option
if include_redacted_emails:
    console.print('\n\n', Panel(Text("Emails Whose Senders Were Redacted", justify='center', style='bold reverse')), '\n')

    for filename, contents in redacted_emails.items():
        console.print(Panel(archive_link(filename), expand=False))
        console.print(escape(cleanup_email_txt(contents)), '\n\n')


if not is_debug:
    console.save_html(OUTPUT_GH_PAGES_HTML, inline_styles=False, clear=False, code_format=CONSOLE_HTML_FORMAT)
    console.print(f"\nWrote HTML to '{OUTPUT_GH_PAGES_HTML}'.")
else:
    console.print(f"\nNot writing HTML because DEBUG=true.")
