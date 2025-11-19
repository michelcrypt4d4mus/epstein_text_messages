#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_

Install: 'pip install rich'
    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT/archive ./epstein_chat_logs_reformatter.py'
"""
import json
import re
from collections import defaultdict
from datetime import datetime
from os import environ
from pathlib import Path

from dotenv import load_dotenv
from rich.align import Align
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
load_dotenv()

from util.emails import BAD_EMAILER_REGEX, DETECT_EMAIL_REGEX, extract_email_sender, replace_signature
from util.env import deep_debug, include_redacted_emails, is_debug
from util.file_helper import extract_file_id, load_file, move_json_file
from util.rich import *

OUTPUT_DIR = Path('docs')
OUTPUT_GH_PAGES_HTML = OUTPUT_DIR.joinpath('index.html')
MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')
DATE_FORMAT = "%m/%d/%y %I:%M:%S %p"

sender_counts = defaultdict(int)
emailer_counts = defaultdict(int)
redacted_emails = {}
convos_labeled = 0
files_processed = 0
msgs_processed = 0

print_header()


def print_top_lines(file_text, n = 10, max_chars = 300, in_panel = False):
    "Print first n lines of a file."
    top_text = escape('\n'.join(file_text.split("\n")[0:n])[0:max_chars])
    output = Panel(top_text, expand=False) if in_panel else top_text + '\n'
    console.print(output, style='dim')


def first_timestamp_in_file(file_arg: Path):
    if deep_debug:
        print(f"Getting timestamp from {file_arg}...")

    with open(file_arg) as f:
        for match in MSG_REGEX.finditer(f.read()):
            try:
                timestamp_str = match.group(2).strip()
                return datetime.strptime(timestamp_str, DATE_FORMAT)
            except ValueError as e:
                print(f"[WARNING] Failed to parse '{timestamp_str}' to datetime! Using next match. Error: {e}'")


def get_imessage_log_files() -> list[Path]:
    """Scan text files, count email senders, and return filtered list of iMessage log file paths."""
    docs_dir = environ['EPSTEIN_DOCS_DIR']

    if not docs_dir:
        raise EnvironmentError(f"EPSTEIN_DOCS_DIR env var not set!")

    docs_dir = Path(docs_dir)
    files = [f for f in docs_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
    log_files = []

    for file_arg in files:
        file_text = ''

        if deep_debug:
            console.print(f"Scanning '{file_arg.name}'...", style='dim')

        file_text = load_file(file_arg)
        file_lines = file_text.split('\n')

        if len(file_text) == 0:
            if deep_debug:
                console.print(f"   -> Skipping empty file...", style='dim')

            continue
        elif MSG_REGEX.search(file_text):
            if deep_debug:
                console.print(f"    -> Found iMessage log file", style='dim')

            log_files.append(file_arg)
        elif file_text[0] == '{':  # Check for JSON
            move_json_file(file_arg)
        else:
            emailer = None

            if DETECT_EMAIL_REGEX.match(file_text):  # Handle emails
                emailer_counts['TOTAL'] += 1

                try:
                    emailer = extract_email_sender(file_text) or UNKNOWN
                    emailer = emailer or UNKNOWN
                    is_ok_emailer = not BAD_EMAILER_REGEX.match(emailer)

                    if is_ok_emailer:
                        emailer_counts[emailer.lower()] += 1

                    if len(emailer) >= 3 and emailer != UNKNOWN and is_ok_emailer:
                        continue  # Don't print contents if we found a valid email
                    elif emailer == UNKNOWN:
                        redacted_emails[file_arg.name] = file_text
                except Exception as e:
                    console.print_exception()
                    console.print(f"\nError file '{file_arg.name}' with {len(file_lines)} lines, top lines:")
                    print_top_lines(file_text)
                    raise e

            if is_debug:
                console.print(f"Questionable file '{file_arg.name}' with {len(file_lines)} lines, top lines:")

                if emailer and emailer != UNKNOWN:
                    console.print(f"Failed to find valid email (got '{emailer}')", style='red')

                print_top_lines(file_text)

            continue

    print(f"Found {len(log_files)} iMessage logs out of {len(files)} files in '{docs_dir}'...")
    return sorted(log_files, key=lambda f: first_timestamp_in_file(f))   # Sort by first timestamp


for file_arg in get_imessage_log_files():
    file_text = load_file(file_arg)
    file_lines = file_text.split('\n')
    file_id = extract_file_id(file_arg.name)
    files_processed += 1
    counterparty = UNKNOWN
    counterparty_guess = None
    console.print(Panel(file_arg.name, style='reverse', expand=False))
    file_url = f"{COURIER_NEWSROOM_ARCHIVE}&page=1&q={file_arg}&p=1"
    console.print(f"[link={file_url}]View File in Courier Newsroom Archive[/link]")

    if file_id:
        counterparty = KNOWN_COUNTERPARTY_FILE_IDS.get(file_id, UNKNOWN)

        if counterparty != UNKNOWN:
            hint_txt = Text(f"Found confirmed counterparty ", style='grey')
            hint_txt.append(counterparty, style=COUNTERPARTY_COLORS.get(counterparty, DEFAULT))
            console.print(hint_txt.append(f" for file ID {file_id}...\n"))
        elif file_id in GUESSED_COUNTERPARTY_FILE_IDS:
            counterparty_guess = GUESSED_COUNTERPARTY_FILE_IDS[file_id]
            txt = Text("(This is probably a conversation with ", style='grey')
            txt.append(counterparty_guess, style=f"{COUNTERPARTY_COLORS.get(counterparty_guess, DEFAULT)}")
            console.print(txt.append(')\n'), style='dim')

    if counterparty != UNKNOWN or counterparty_guess is not None:
        convos_labeled += 1

    for i, match in enumerate(MSG_REGEX.finditer(file_text)):
        msgs_processed += 1
        sender = sender_str = match.group(1).strip()
        sender_style = None
        timestamp = Text(f"[{match.group(2).strip()}] ", style='dim')
        msg = match.group(4).strip()
        msg_lines = msg.split('\n')

        if len(sender) > 0:
            if sender == 'e:jeeitunes@gmail.com':
                sender = sender_str = EPSTEIN
            elif sender == '+19174393646':
                sender = sender_str = SCARAMUCCI
            elif sender == '+13109906526':
                sender = sender_str = BANNON
            elif PHONE_NUMBER_REGEX.match(sender):
                sender_style = PHONE_NUMBER
            elif re.match('[ME]+', sender):
                sender = MELANIE_WALKER
        else:
            if counterparty != UNKNOWN:
                sender = sender_str = counterparty
            elif counterparty_guess is not None:
                sender = counterparty_guess
                sender_str = f"{counterparty_guess} (?)"
            else:
                sender = sender_str = UNKNOWN

        if re.match('[-_1]+|[4Ide]', sender):
            sender_counts[UNKNOWN] += 1
        else:
            sender_counts[sender] += 1

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
            msg = Text('').append(link_text, style='deep_sky_blue4 underline')

            if len(msg_lines) > 0:
                msg = msg.append('\n' + ' '.join(msg_lines))
        else:
            msg = msg.replace('\n', ' ')  # remove newlines

        console.print(Text('').append(timestamp).append(sender_txt).append(': ', style='dim').append(msg))

    console.line(2)


# Text message counts
counts_table = Table(title="Message Counts By Sender", show_header=True, header_style="bold")
counts_table.add_column("Sender", style="steel_blue bold", justify="left", width=30)
counts_table.add_column("Message Count", justify="center")

for k, v in sorted(sender_counts.items(), key=lambda item: item[1], reverse=True):
    counts_table.add_row(Text(k, COUNTERPARTY_COLORS.get(k, 'grey23 bold')), str(v))

console.print(counts_table)
console.print(f"\nProcessed {files_processed} log files with {msgs_processed} text messages ({convos_labeled} deanonymized conversations)")
console.print(f"(Last deploy found 77 files with 4668 messages)\n", style='dim')

# Email sender counts
console.line(2)
num_potential_emails = emailer_counts.pop('TOTAL')
counts_table = Table(title="Email Counts By Sender", show_header=True, header_style="bold")
counts_table.add_column("From", style="steel_blue bold", justify="left", width=40)
counts_table.add_column("Email Count", justify="center")

for k, v in sorted(emailer_counts.items(), key=lambda item: item[1], reverse=True):
    counts_table.add_row(Text(k), str(v))

console.print(counts_table)
console.print(f"Scanned {num_potential_emails} potential emails, found {sum([i for i in emailer_counts.values()])} senders.")

# Redacted emails option
if include_redacted_emails:
    console.print(Panel(Text("Redacted Emails", justify='center', style='bold reverse')), '\n')

    for filename, contents in redacted_emails.items():
        console.print(Panel(filename, expand=False))
        console.print(escape(replace_signature(contents)), '\n\n', style='dim')


if not is_debug:
    console.save_html(OUTPUT_GH_PAGES_HTML, inline_styles=False, clear=False, code_format=CONSOLE_HTML_FORMAT)
    console.print(f"Wrote HTML to '{OUTPUT_GH_PAGES_HTML}'.")
else:
    console.print(f"\nNot writing HTML because DEBUG=true.")
