#!/usr/bin/env python
"""
Reformat Epstein text message file form for readability. Requires python.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_
Can handle being called on multiple filenames and/or wildcards.

Install: 'pip install rich'
    Run: 'python epstein_chat_logs_reformatter.py [TEXT_MESSAGE_FILENAMES]'
"""
import csv
import json
import re
from collections import defaultdict
from datetime import datetime
from io import StringIO
from os import environ
from pathlib import Path

from dotenv import load_dotenv
from rich.align import Align
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
load_dotenv()

from util.emails import BAD_EMAILER_REGEX, DETECT_EMAIL_REGEX, extract_email_sender
from util.env import deep_debug, is_debug
from util.file_helper import load_file, move_json_file


CONSOLE_HTML_FORMAT = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{stylesheet}

body {{
    color: {foreground};
    background-color: {background};
}}
</style>
</head>
<body>
    <pre style="font-family: Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace; white-space: pre-wrap; overflow-wrap: break-word;">
        <code style="font-family: inherit; white-space: pre-wrap; overflow-wrap: break-word;">
            {code}
        </code>
    </pre>
</body>
</html>
"""

#  of who is the counterparty in each file
AI_COUNTERPARTY_DETERMINATION_TSV = StringIO("""
filename	counterparty	source
HOUSE_OVERSIGHT_025400.txt	Steve Bannon (likely)	Trump NYT article criticism; Hannity media strategy
HOUSE_OVERSIGHT_025408.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025452.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025479.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_025707.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025734.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027260.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027281.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027346.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027365.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027374.txt	Steve Bannon	China strategy and geopolitics
HOUSE_OVERSIGHT_027406.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027440.txt	Michael Wolff	Trump book/journalism project
HOUSE_OVERSIGHT_027445.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027455.txt	Steve Bannon (likely)	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027460.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027515.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027536.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027655.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027707.txt	Steve Bannon	Italian politics; Trump discussions
HOUSE_OVERSIGHT_027722.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027735.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027794.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_029744.txt	Steve Bannon (likely)	Trump and New York Times coverage
HOUSE_OVERSIGHT_031045.txt	Steve Bannon (likely)	Trump and New York Times coverage""".strip())

OUTPUT_DIR = Path('docs')
OUTPUT_GH_PAGES_HTML = OUTPUT_DIR.joinpath('index.html')
OUTPUT_WIDTH = 120

FILE_ID_REGEX = re.compile(r'.*HOUSE_OVERSIGHT_(\d+)\.txt')
MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
PHONE_NUMBER_REGEX = re.compile(r'^[\d+]+.*')
DATE_FORMAT = "%m/%d/%y %I:%M:%S %p"

PHONE_NUMBER = 'phone_number'
ANIL = "Anil Ambani"
BANNON = 'Bannon'
DEFAULT = 'default'
EPSTEIN = 'Epstein'
MELANIE_WALKER = 'Melanie Walker'
MIROSLAV = 'Miroslav Lajčák'
PLASKETT = 'Stacey Plaskett'
SCARAMUCCI = 'The Mooch'
SOON_YI = 'Soon-Yi Previn'
SUMMERS = 'Larry Summers'
TERJE = 'Terje Rød-Larsen'
UNKNOWN = '(unknown)'

# Color different counterparties differently
COUNTERPARTY_COLORS = {
    ANIL: 'dark_green',
    BANNON: 'color(58)',
    'Celina Dubin': 'medium_orchid1',
    DEFAULT: 'wheat4',
    EPSTEIN: 'blue',
    'Eva': 'orchid',
    'Joi Ito': 'blue_violet',
    MELANIE_WALKER: 'deep_pink3',
    MIROSLAV: 'slate_blue3',
    "Michael Wolff": 'grey54',
    PHONE_NUMBER: 'bright_green',
    PLASKETT: 'medium_orchid3',
    SCARAMUCCI: 'orange1',
    SOON_YI: 'hot_pink',
    SUMMERS: 'bright_red',
    TERJE: 'light_slate_blue',
    UNKNOWN: 'cyan',
}

KNOWN_COUNTERPARTY_FILE_IDS = {
    '025707': BANNON,
    '025734': BANNON,
    '025452': BANNON,
    '025408': BANNON,
    '027307': BANNON,
    '027515': MIROSLAV,        # https://x.com/ImDrinknWyn/status/1990210266114789713
    '025429': PLASKETT,
    '027777': SUMMERS,
    '027165': MELANIE_WALKER,  # https://www.wired.com/story/jeffrey-epstein-claimed-intimate-knowledge-of-donald-trumps-views-in-texts-with-bill-gates-adviser/
    '027128': SOON_YI,         # https://x.com/ImDrinknWyn/status/1990227281101434923
    '027217': SOON_YI,         # refs marriage to woody allen
    '027244': SOON_YI,         # refs Woody
    '027257': SOON_YI,         # 'Woody Allen' in Participants: field
    '027333': SCARAMUCCI,      # unredacted phone number
    '027278': TERJE,
    '027255': TERJE,
    '031173': 'Ards',          # Participants: field, possibly incomplete
    '031042': ANIL,            # Participants: field
    '027225': ANIL,            # Birthday
    '027401': 'Eva',           # Participants: field
    '027650': 'Joi Ito',       # Participants: field
}

GUESSED_COUNTERPARTY_FILE_IDS = {
    '025363': BANNON,          # Trump and New York Times coverage
    '025368': BANNON,          # Trump and New York Times coverage
    '027585': BANNON,          # Tokyo trip
    '027568': BANNON,
    '027695': BANNON,
    '027594': BANNON,
    '027720': BANNON,          # first 3 lines of 027722
    '027549': BANNON,
    '027434': BANNON,          # References Maher appearance
    '027764': BANNON,
    '027576': MELANIE_WALKER,  # https://www.ahajournals.org/doi/full/10.1161/STROKEAHA.118.023700
    '027141': MELANIE_WALKER,
    '027232': MELANIE_WALKER,
    '027133': MELANIE_WALKER,
    '027184': MELANIE_WALKER,
    '027214': MELANIE_WALKER,
    '027148': MELANIE_WALKER,
    '027396': SCARAMUCCI,
    '031054': SCARAMUCCI,
    '027221': ANIL,
    '025436': 'Celina Dubin',
}

for counterparty in COUNTERPARTY_COLORS:
    COUNTERPARTY_COLORS[counterparty] = f"{COUNTERPARTY_COLORS[counterparty]} bold"


def extract_file_id(filename) -> str:
    file_match = FILE_ID_REGEX.match(str(filename))

    if file_match:
        return file_match.group(1)
    else:
        raise RuntimeError(f"Failed to extract file ID from {filename}")


for row in csv.DictReader(AI_COUNTERPARTY_DETERMINATION_TSV, delimiter='\t'):
    file_id = extract_file_id(row['filename'].strip())
    counterparty = row['counterparty'].strip()
    counterparty = BANNON if counterparty.startswith('Steve Bannon') else counterparty

    if file_id in GUESSED_COUNTERPARTY_FILE_IDS:
        raise RuntimeError(f"Can't overwrite attribution of {file_id} to {GUESSED_COUNTERPARTY_FILE_IDS[file_id]} with {counterparty}")

    GUESSED_COUNTERPARTY_FILE_IDS[file_id] = counterparty.replace(' (likely)', '').strip()


sender_counts = defaultdict(int)
emailer_counts = defaultdict(int)
convos_labeled = 0
files_processed = 0
msgs_processed = 0

# Start output
console = Console(color_system='256', theme=Theme(COUNTERPARTY_COLORS), width=OUTPUT_WIDTH)
console.record = True
console.line()

console.print(Panel(Text(
    "Oversight Committee Releases Additional Epstein Estate Documents"
    "\nhttps://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/"
    "\n\nEpstein Estate Documents - Seventh Production",
    justify='center',
    style='bold reverse'
)))

console.line()
console.print(Align.center("[link=https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great]I Made Epstein's Text Messages Great Again (And You Should Read Them)[/link]"))
console.print(Align.center("https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great"))
console.print(Align.center("[link=https://cryptadamus.substack.com/]Substack[/link]"))
console.print(Align.center("[link=https://universeodon.com/@cryptadamist]Mastodon[/link]"))
console.print(Align.center("[link=https://x.com/Cryptadamist/status/1990866804630036988]Twitter[/link]"))

# Translation helper
table = Table(title="Abbreviations Used Frequently In These Chats", show_header=True, header_style="bold")
table.add_column("Abbreviation", style="steel_blue bold", justify="center", width=19)
table.add_column("Translation", style="deep_sky_blue4", justify="center")
table.add_row("AD", "Abu Dhabi")
table.add_row("Barak", "Ehud Barak (Former Israeli prime minister)")
table.add_row("Barrack", "Tom Barrack")
table.add_row('BG', "Bill Gates")
table.add_row('Bill', "Bill Gates")
table.add_row("Brock", "Brock Pierce")
table.add_row("DB", "Deutsche Bank (maybe??)")
table.add_row('HBJ', "Hamad bin Jassim (Former Qatari Prime Minister)")
table.add_row('Jagland', 'Thorbjørn Jagland')
table.add_row("Hoffenberg', 'Steven Hoffenberg (Epstein's partner in old ponzi scheme)")
table.add_row('KSA', "Kingdom of Saudi Arabia")
table.add_row('MBS', "Mohammed bin Salman Al Saud (Saudi ruler)")
table.add_row('Jared', "Jared Kushner")
table.add_row("Miro", MIROSLAV)
table.add_row("Mooch", "Anthony 'The Mooch' Scaramucci (Skybridge Capital)")
table.add_row("Terje", TERJE)
table.add_row("Woody", "Woody Allen")
table.add_row("Zug", "City in Switzerland known as a crypto hot spot")
console.print('\n', Align.center(table))
console.line(2)
console.print(Align.center("Conversations are sorted chronologically based on timestamp of first message."), style='bold dark_green')
console.print(Align.center(f"If you think there's an attribution error or can deanonymize or confirm an {UNKNOWN} or (?) individual contact @cryptadamist."), style='dim')
console.line(2)


def print_top_lines(file_text, n = 10, max_chars = 250, in_panel = False):
    top_text = escape('\n'.join(file_text.split("\n")[0:n])[0:max_chars])
    output = Panel(top_text, expand=False) if in_panel else top_text + '\n'
    console.print(output, style='dim')


if deep_debug:
    console.print('KNOWN_COUNTERPARTY_FILE_IDS\n--------------')
    console.print(json.dumps(KNOWN_COUNTERPARTY_FILE_IDS))
    console.print('\n\n\nGUESSED_COUNTERPARTY_FILE_IDS\n--------------')
    console.print_json(json.dumps(GUESSED_COUNTERPARTY_FILE_IDS))
    console.line(2)


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
                    emailer_counts[emailer.lower()] += 1

                    if len(emailer) >= 3 and emailer != UNKNOWN and not BAD_EMAILER_REGEX.match(emailer):
                        continue  # Don't print contents if we found a valid email
                except Exception as e:
                    console.print_exception()
                    console.print(f"\nError file '{file_arg.name}' with {len(file_lines)} lines, top lines:")
                    print_top_lines(file_text)
                    raise e

            if is_debug:
                console.print(f"Questionable file '{file_arg.name}' with {len(file_lines)} lines, top lines:")

                if emailer:
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
                sender = SCARAMUCCI
            elif sender == '+13109906526':
                sender = BANNON
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


counts_table = Table(title="Message Counts By Sender", show_header=True, header_style="bold")
counts_table.add_column("Sender", style="steel_blue bold", justify="left", width=30)
counts_table.add_column("Message Count", justify="center")

for k, v in sorted(sender_counts.items(), key=lambda item: item[1], reverse=True):
    counts_table.add_row(Text(k, COUNTERPARTY_COLORS.get(k, 'grey23 bold')), str(v))

console.print(counts_table)
console.print(f"\nProcessed {files_processed} log files with {msgs_processed} text messages ({convos_labeled} deanonymized conversations)")
console.print(f"(Last deploy found 77 files with 4668 messages)\n", style='dim')


console.line(2)
num_potential_emails = emailer_counts.pop('TOTAL')
counts_table = Table(title="Email Counts By Sender", show_header=True, header_style="bold")
counts_table.add_column("From", style="steel_blue bold", justify="left", width=40)
counts_table.add_column("Email Count", justify="center")

for k, v in sorted(emailer_counts.items(), key=lambda item: item[1], reverse=True):
    counts_table.add_row(Text(k), str(v))

console.print(counts_table)
console.print(f"Scanned {num_potential_emails} potential emails, found {sum([i for i in emailer_counts.values()])} senders.")


if not is_debug:
    console.save_html(OUTPUT_GH_PAGES_HTML, inline_styles=False, clear=False, code_format=CONSOLE_HTML_FORMAT)
    console.print(f"Wrote HTML to '{OUTPUT_GH_PAGES_HTML}'.")
else:
    console.print(f"\nNot writing HTML because DEBUG=true.")
