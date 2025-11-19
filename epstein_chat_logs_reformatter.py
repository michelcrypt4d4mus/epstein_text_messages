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
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
load_dotenv()

#  of who is the counterparty in each file
AI_COUNTERPARTY_DETERMINATION_TSV = StringIO("""
filename	counterparty	source
HOUSE_OVERSIGHT_025400.txt	Steve Bannon (likely)	Trump NYT article criticism; Hannity media strategy
HOUSE_OVERSIGHT_025403.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_025408.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025423.txt	unclear	unclear
HOUSE_OVERSIGHT_025426.txt	unclear	unclear
HOUSE_OVERSIGHT_025429.txt	Stacey Plaskett	Michael Cohen congressional testimony coordination
HOUSE_OVERSIGHT_025452.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025479.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_025707.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_025734.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_025735.txt	Unidentified	unclear
HOUSE_OVERSIGHT_027128.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027214.txt	unclear	unclear
HOUSE_OVERSIGHT_027217.txt	Business associate	Business discussions
HOUSE_OVERSIGHT_027225.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027248.txt	unclear	unclear
HOUSE_OVERSIGHT_027250.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027260.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027275.txt	unclear	unclear
HOUSE_OVERSIGHT_027278.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027281.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027330.txt	unclear	unclear
HOUSE_OVERSIGHT_027333.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027346.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027365.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027374.txt	Steve Bannon	China strategy and geopolitics
HOUSE_OVERSIGHT_027396.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027406.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027428.txt	unclear	unclear
HOUSE_OVERSIGHT_027434.txt	Business associate	Business discussions
HOUSE_OVERSIGHT_027440.txt	Michael Wolff	Trump book/journalism project
HOUSE_OVERSIGHT_027445.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027452.txt	unclear	unclear
HOUSE_OVERSIGHT_027455.txt	Steve Bannon (likely)	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027460.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027515.txt	Personal contact	Personal/social plans
HOUSE_OVERSIGHT_027536.txt	Steve Bannon	China strategy and geopolitics; Trump discussions
HOUSE_OVERSIGHT_027585.txt	Business associate	Business discussions
HOUSE_OVERSIGHT_027655.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027707.txt	Steve Bannon	Italian politics; Trump discussions
HOUSE_OVERSIGHT_027722.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027735.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_027794.txt	Steve Bannon	Trump and New York Times coverage
HOUSE_OVERSIGHT_029744.txt	Steve Bannon (likely)	Trump and New York Times coverage
HOUSE_OVERSIGHT_031045.txt	Steve Bannon (likely)	Trump and New York Times coverage
HOUSE_OVERSIGHT_031054.txt	Personal contact	Personal/social plans
""".strip())

OUTPUT_BASENAME = "epstein_text_msgs_7th_production_colorized_and_deanonymized"
OUTPUT_DIR = Path('docs')
OUTPUT_GH_PAGES_HTML = OUTPUT_DIR.joinpath('index.html')

MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
FILE_ID_REGEX = re.compile(r'.*HOUSE_OVERSIGHT_(\d+)\.txt')
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
    '027257': SOON_YI,  # 'Woody Allen',   # Participants: field
    '027333': SCARAMUCCI,      # unredacted phone number
    '027278': TERJE,
    '027255': TERJE,
    '031173': 'Ards',          # Participants: field, possibly incomplete
    '031042': ANIL,            # Participants: field
    '027225': ANIL,            # Birthday
    '027650': 'Joi Ito',       # Participants: field
    '027401': 'Eva',           # Participants: field
}

GUESSED_COUNTERPARTY_FILE_IDS = {
    '025363': BANNON,          # Trump and New York Times coverage
    '025368': BANNON,          # Trump and New York Times coverage
    '027568': BANNON,
    '027695': BANNON,
    '027594': BANNON,
    '027720': BANNON,          # first 3 lines of 027722
    '027549': BANNON,
    '027434': BANNON,          # References Maher appearance
    '027764': BANNON,
    '027396': BANNON,
    '027576': MELANIE_WALKER,  # https://www.ahajournals.org/doi/full/10.1161/STROKEAHA.118.023700
    '027141': MELANIE_WALKER,
    '027232': MELANIE_WALKER,
    '027133': MELANIE_WALKER,
    '027184': MELANIE_WALKER,
    '027214': MELANIE_WALKER,
    '027148': MELANIE_WALKER,
    '027396': SCARAMUCCI,
    '031054': SCARAMUCCI,
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

    if counterparty in ['unclear', 'Unidentified', 'Personal contact', 'Business associate']:
        continue
    else:
        if file_id in GUESSED_COUNTERPARTY_FILE_IDS:
            raise RuntimeError(f"Can't overwrite attribution of {file_id} to {GUESSED_COUNTERPARTY_FILE_IDS[file_id]} with {counterparty}")

        GUESSED_COUNTERPARTY_FILE_IDS[file_id] = counterparty.replace(' (likely)', '').strip()


is_debug = len(environ.get('DEBUG') or '') > 0
sender_counts = defaultdict(int)
emailer_counts = defaultdict(int)
convos_labeled = 0
files_processed = 0
msgs_processed = 0

console = Console(color_system='256', theme=Theme(COUNTERPARTY_COLORS))
console.record = True

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


if is_debug:
    console.print('KNOWN_COUNTERPARTY_FILE_IDS\n--------------')
    console.print(json.dumps(KNOWN_COUNTERPARTY_FILE_IDS))
    console.print('\n\n\nGUESSED_COUNTERPARTY_FILE_IDS\n--------------')
    console.print_json(json.dumps(GUESSED_COUNTERPARTY_FILE_IDS))
    console.line(2)


def first_timestamp_in_file(file_arg: Path):
    if is_debug:
        console.log(f"Getting timestamp from {file_arg}")

    with open(file_arg) as f:
        for match in MSG_REGEX.finditer(f.read()):
            try:
                timestamp_str = match.group(2).strip()
                return datetime.strptime(timestamp_str, DATE_FORMAT)
            except ValueError as e:
                print(f"[WARNING] Failed to parse '{timestamp_str}' to datetime! Using next match. Error: {e}'")


EMAIL_REGEX = re.compile(r'From: (.*)')
BROKEN_EMAIL_REEGEX = re.compile(r'^From:\s*\nSent:\s*\nTo:\s*\n(CC:\s*\n)?Subject:\s*\n(Importance:\s*\n)?(Attachments:\s*\n)?([\w ]{2,})\n')
EPSTEIN_EMAIL_REGEX = re.compile(r'jee[vy]acation[©@]|jeffrey E\.|Jeffrey Epstein', re.IGNORECASE)
GHISLAINE_EMAIL_REGEX = re.compile(r'gmax', re.IGNORECASE)
EHUD_BARAK_EMAIL_REGEX = re.compile(r'(ehud|h)\s*barak', re.IGNORECASE)
BANNON_EMAIL_REGEX = re.compile(r'steve bannon', re.IGNORECASE)
LARRY_SUMMERS_EMAIL_REGEX = re.compile(r'La(wrence|rry).*Summers', re.IGNORECASE)
DATE_REGEX = re.compile(r'^Date:\s*(.*)\n')


def tally_email(file_text):
    email_match = EMAIL_REGEX.search(file_text)
    broken_match = BROKEN_EMAIL_REEGEX.search(file_text)
    date_match = DATE_REGEX.search(file_text)
    emailer = None

    if broken_match:
        emailer = broken_match.group(3) or broken_match.group(2) or broken_match.group(1)
    else:
        emailer = email_match.group(1)

    if not emailer:
        if is_debug:
            console.print(f"Failed to find a match!")
            return

    try:
        emailer = emailer.strip().strip('_').strip('[').strip(']').strip('<').strip()
    except Exception as e:
        console.print_exception()
        console.print('\nFailed rows:')
        console.print('\n'.join(file_text.split("\n")[0:10]))
        raise e

    if EPSTEIN_EMAIL_REGEX.search(emailer):
        emailer = 'Jeffrey Epstein'
    elif GHISLAINE_EMAIL_REGEX.search(emailer):
        emailer = 'Ghislaine Maxwell'
    elif emailer == 'ji@media.mitedu' or 'joichi ito' in emailer.lower():
        emailer = 'Joi Ito'
    elif EHUD_BARAK_EMAIL_REGEX.search(emailer):
        emailer = 'Ehud Barak'
    elif BANNON_EMAIL_REGEX.search(emailer):
        emailer = 'Steve Bannon'
    elif LARRY_SUMMERS_EMAIL_REGEX.search(emailer):
        emailer = 'Larry Summers'
    elif 'paul krassner' in emailer.lower():
        emailer = 'Paul Krassner'

    if is_debug:
        console.print(f"Handling email from '{emailer}'...")

    emailer_counts[emailer.lower()] += 1
    return emailer


def get_imessage_log_files() -> list[Path]:
    docs_dir = environ['EPSTEIN_DOCS_DIR']

    if not docs_dir:
        raise EnvironmentError(f"EPSTEIN_DOCS_DIR env var not set!")

    docs_dir = Path(docs_dir)
    files = [f for f in docs_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
    log_files = []

    for file_arg in files:
        file_text = ''

        if is_debug:
            console.print(f"Checking '{file_arg.name}'...", style='dim')

        with open(file_arg) as f:
            file_text = f.read()
            file_text = file_text[1:] if (len(file_text) > 0 and file_text[0] == '\ufeff') else file_text  # remove BOM

        if MSG_REGEX.search(file_text):
            log_files.append(file_arg)
        else:
            file_lines = file_text.split('\n')

            # Handle emails
            if 'From: ' in file_lines[0] or (len(file_lines) > 2 and ('From: ' in file_lines[1] or 'From: ' in file_lines[2])) or DATE_REGEX.match(file_lines[0]):
                try:
                    emailer = tally_email(file_text) or ''

                    if 'Sent' in emailer:
                        console.print('First char:', emailer[0])
                        console.print(emailer[0])
                        console.print(f"startwith Sent = {emailer.startswith('Sent')}")

                    if len(emailer) >= 3 and not emailer.startswith('Sent'):
                        continue
                except Exception as e:
                    console.print_exception()
                    console.print(f"\nError file '{file_arg.name}' with {len(file_lines)} lines, top lines:")
                    console.print('\n'.join(file_lines[0:10]) + '\n', style='dim')
                    raise e

            if is_debug:
                if len(file_text) > 1 and file_text[1] == '{':  # Check for JSON
                    json_subdir_path = file_arg.parent.joinpath('json_files').joinpath(file_arg.name + '.json')
                    console.print(f"'{file_arg}' looks like JSON, moving to '{json_subdir_path}'\n", style='yellow1 bold')
                    file_arg.rename(json_subdir_path)
                else:
                    console.print(f"'Skipping file '{file_arg.name}' with {len(file_lines)} lines, top lines:")
                    console.print('\n'.join(file_lines[0:10]) + '\n', style='dim')

            continue

    print(f"Found {len(log_files)} iMessage logs out of {len(files)} files in '{docs_dir}'...")
    return sorted(log_files, key=lambda f: first_timestamp_in_file(f))   # Sort by first timestamp


for file_arg in get_imessage_log_files():
    with open(file_arg) as f:
        file_basename = file_arg.name
        file_lines = [l.strip() for l in f.read().split('\n') if not l.startswith('HOUSE OVERSIGHT')]
        file_text = '\n'.join(file_lines)

        files_processed += 1
        console.print(Panel(file_basename, style='reverse', expand=False))
        file_id = extract_file_id(file_basename)
        counterparty = UNKNOWN
        counterparty_guess = None

        if file_id:
            counterparty = KNOWN_COUNTERPARTY_FILE_IDS.get(file_id, UNKNOWN)

            if counterparty != UNKNOWN:
                hint_txt = Text(f"Found known counterparty ", style='dim')
                hint_txt.append(counterparty, style=COUNTERPARTY_COLORS.get(counterparty, DEFAULT))
                console.print(hint_txt.append(f" for file ID {file_id}...\n"))
            elif file_id in GUESSED_COUNTERPARTY_FILE_IDS:
                counterparty_guess = GUESSED_COUNTERPARTY_FILE_IDS[file_id]
                txt = Text("(This might be a conversation with ", style='grey')
                txt.append(counterparty_guess, style=f"{COUNTERPARTY_COLORS.get(counterparty_guess, DEFAULT)}")
                console.print(txt.append(' according to AI)\n'))

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

console.print(counts_table, '\n\n')
console.print(f"Processed {files_processed} log files with {msgs_processed} text messages ({convos_labeled} deanonymized conversations)")
console.print(f"(Last deploy found 77 files with 4668 messages)\n", style='dim')


console.line(2)
counts_table = Table(title="Email Counts By Sender", show_header=True, header_style="bold")
counts_table.add_column("From", style="steel_blue bold", justify="left")
counts_table.add_column("Email Count", justify="center")

for k, v in sorted(emailer_counts.items(), key=lambda item: item[1], reverse=True):
    counts_table.add_row(Text(k), str(v))

console.print(counts_table, '\n\n')


if not is_debug:
    console.save_html(OUTPUT_GH_PAGES_HTML, inline_styles=True, clear=False)
    console.print(f"Wrote HTML to '{OUTPUT_GH_PAGES_HTML}'.")
else:
    console.print(f"\nNot writing HTML because DEBUG=true.")
