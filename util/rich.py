import csv
import json
import logging
import re
import urllib.parse

from rich.align import Align
from rich.console import Console
from rich.logging import RichHandler
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .constants import *
from .env import deep_debug, is_debug
from .file_helper import extract_file_id

LEADING_WHITESPACE_REGEX = re.compile(r'\A\s*', re.MULTILINE)
MAX_PREVIEW_CHARS = 300
OUTPUT_WIDTH = 120

ARAB_COLOR = 'dark_green'
ARCHIVE_LINK = 'archive_link'
ARCHIVE_LINK_COLOR = 'blue3'
PHONE_NUMBER = 'phone_number'
TEXT_LINK = 'text_link'

CONSOLE_HTML_FORMAT = """<!DOCTYPE html>
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

NAMES_TO_NOT_COLOR = [
    'Black',
    'David',
    'Michael',
    'Robert',
    'Steve',
    'The',
    'Victor',
]

# Color different counterparties differently
COUNTERPARTY_COLORS = {
    ANIL: 'dark_green',
    ARCHIVE_LINK: 'deep_sky_blue4',
    ARIANE_DE_ROTHSCHILD: 'indian_red',
    'Celina Dubin': 'medium_orchid1',
    DEFAULT: 'wheat4',
    DONALD_TRUMP: 'red3',
    JEFFREY_EPSTEIN: 'blue',
    EVA: 'orchid',
    LARRY_SUMMERS: 'dark_magenta',
    MELANIE_WALKER: 'deep_pink3',
    MIROSLAV: 'slate_blue3',
    "Michael Wolff": 'grey54',
    'Noam Chomsky': 'grey23',
    PHONE_NUMBER: 'bright_green',
    PLASKETT: 'medium_orchid3',
    ROBERT_TRIVERS: 'blue_violet',
    SCARAMUCCI: 'orange1',
    SOON_YI: 'hot_pink',
    STEVE_BANNON: 'color(58)',
    TERJE: 'light_slate_blue',
    TEXT_LINK: 'deep_sky_blue4 underline',
    UNKNOWN: 'cyan',
    'Victor Orban': 'purple4',
}

PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED = {
    None: 'grey74',
    STEVE_BANNON: COUNTERPARTY_COLORS[STEVE_BANNON],
    'Sean Bannon': COUNTERPARTY_COLORS[STEVE_BANNON],
    JOI_ITO: 'blue_violet',
    AL_SECKEL: 'orange_red1',
    EHUD_BARAK: 'chartreuse4',
}

PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES = {
    'Deepak Chopra': 'dark_goldenrod',
    GHISLAINE_MAXWELL: 'deep_pink3',
    LEON_BLACK: 'dark_cyan',
    LANDON_THOMAS: 'misty_rose3',  # FT journo
    SULTAN_BIN_SULAYEM: 'green1',
    # Epstein's lawyers
    DARREN_INDYKE: 'purple3',
    'Richard Kahn': 'purple4',
}

COUNTERPARTY_COLORS.update(PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED)
COUNTERPARTY_COLORS.update(PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES)
COURIER_NEWSROOM_ARCHIVE = 'https://journaliststudio.google.com/pinpoint/search?collection=092314e384a58618'
COFFEEZILLA_ARCHIVE = 'https://journaliststudio.google.com/pinpoint/search?collection=061ce61c9e70bdfd'

epsteinify_url = lambda name: f"https://epsteinify.com/?name={urllib.parse.quote(name)}"
search_archive_url = lambda txt: f"{COURIER_NEWSROOM_ARCHIVE}&q={urllib.parse.quote(txt)}&p=1"
search_coffeezilla_url = lambda txt: f"{COFFEEZILLA_ARCHIVE}&q={urllib.parse.quote(txt)}&p=1"

logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("rich")

if deep_debug:
    logger.setLevel(logging.DEBUG)
elif is_debug:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)

console = Console(color_system='256', theme=Theme(COUNTERPARTY_COLORS), width=OUTPUT_WIDTH)
console.record = True

# This is after the Theme() instantiation because 'bg' is reserved'
COUNTERPARTY_COLORS.update({
    'bg': 'turquoise4',
    'Clinton': 'sky_blue1',
    'DJT': COUNTERPARTY_COLORS[DONALD_TRUMP],
    'Dubai': ARAB_COLOR,
    'ehbarak': COUNTERPARTY_COLORS[EHUD_BARAK],
    'Israel': 'dodger_blue2',
    'Israeli': 'dodger_blue2',
    'Ivanka': 'medium_violet_red',
    'Jared Kushner': 'medium_violet_red',
    'gmax1@ellmax.com': COUNTERPARTY_COLORS[GHISLAINE_MAXWELL],
    'jeevacation@gmail.com': COUNTERPARTY_COLORS[JEFFREY_EPSTEIN],
    'Qatar': ARAB_COLOR,
    'Qatari': ARAB_COLOR,
    'Scaramucci': COUNTERPARTY_COLORS[SCARAMUCCI],
    'Miro': COUNTERPARTY_COLORS[MIROSLAV],
    'UAE': ARAB_COLOR,
    'Yemen': ARAB_COLOR,
    'Yemeni': ARAB_COLOR,
})


def make_link(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(f"[underline][bold][{style}][link={url}]{link_text}[/link][/{style}][/bold][/underline]")


def archive_link(filename: str, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
    return make_link(search_archive_url(filename), link_txt or filename, style)


def coffeezilla_link(search_term: str, link_txt: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return make_link(search_archive_url(search_term), link_txt or search_term, style)


def highlight_names(text: str) -> str:
    for name, style in COUNTERPARTY_COLORS.items():
        if name is None or name == DEFAULT:
            continue

        name_regex = re.compile(rf"\b({name})\b", re.IGNORECASE)
        text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

        if ' ' not in name:
            continue

        names = name.split(' ')
        last_name = names[-1]
        first_name = ' '.join(names[0:-1])

        # highlight last names
        if last_name not in NAMES_TO_NOT_COLOR:
            name_regex = re.compile(rf"(?!{first_name} ?)\b({last_name}s?)\b", re.IGNORECASE)
            text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

        # highlight first names
        if len(first_name) > 2 and first_name not in NAMES_TO_NOT_COLOR:
            name_regex = re.compile(rf"\b({first_name}s?)\b(?! ?{last_name})", re.IGNORECASE)
            text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

    return text


def print_header():
    console.print(f"This site is not optimized for mobile but if you get past the header it should work ok.", style='dim')
    console.line()
    console.print(Panel(Text("Epstein Estate Documents - Seventh Production Collection Reformatted Text Messages", justify='center', style='bold reverse')))
    console.line()
    console.print(Align.center("[bold][link=https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great]I Made Epstein's Text Messages Great Again (And You Should Read Them)[/link][/bold]"))
    console.print(Align.center("https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great"))
    console.print(Align.center("[link=https://cryptadamus.substack.com/]Substack[/link]"))
    console.print(Align.center("[link=https://universeodon.com/@cryptadamist]Mastodon[/link]"))
    console.print(Align.center("[link=https://x.com/Cryptadamist/status/1990866804630036988]Twitter[/link]"))
    # Acronym table
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
    table.add_row('HBJ', "Hamad bin Jassim (Former Qatari prime minister)")
    table.add_row('Jagland', 'Thorbjørn Jagland')
    table.add_row("Hoffenberg", "Steven Hoffenberg (Epstein's ponzi scheme partner)")
    table.add_row('KSA', "Kingdom of Saudi Arabia")
    table.add_row('MBS', "Mohammed bin Salman Al Saud (Saudi ruler)")
    table.add_row('Jared', "Jared Kushner")
    table.add_row("Miro", MIROSLAV)
    table.add_row("Mooch", "Anthony 'The Mooch' Scaramucci (Skybridge crypto bro)")
    table.add_row("Terje", TERJE)
    table.add_row("Woody", "Woody Allen")
    table.add_row("Zug", "City in Switzerland (crypto hub)")
    console.print('\n', Align.center(table))
    console.line()
    console.print(Align.center(f"[link=https://oversight.house.gov/release/oversight-committee-releases-additional-epstein-estate-documents/]Oversight Committee Releases Additional Epstein Estate Documents[/link]"))
    console.print(Align.center(f"[link={COFFEEZILLA_ARCHIVE}]Coffeezilla Archive Of Raw Epstein Materials[/link]"))
    console.print(Align.center("[link=https://jmail.world]Jmail[/link] (read His Emails via Gmail interface)"))
    console.print(Align.center(f"[link={COURIER_NEWSROOM_ARCHIVE}]Courier Newsroom's Searchable Archive[/link]"))
    console.print(Align.center("[link=https://epsteinify.com/names]epsteinify.com[/link] (raw document images)"))
    console.print(Align.center("[link=https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_]Google Drive Raw Documents[/link]"))
    console.line(2)
    console.print(Align.center("Conversations are sorted chronologically based on timestamp of first message."), style='bold dark_green')
    console.print(Align.center(f"If you think there's an attribution error or can deanonymize an {UNKNOWN} contact @cryptadamist."), style='dim')
    console.line(2)


def print_email_table(counts: dict[str, int], column_title: str) -> None:
    counts_table = Table(title=f"Email Counts By {column_title}", show_header=True, header_style="bold")
    counts_table.add_column(column_title, justify="left")
    counts_table.add_column("Email Count", justify="center")

    for k, v in sorted(counts.items(), key=lambda item: [item[1], item[0]], reverse=True):
        k = k.title() if ' ' in k else k
        counts_table.add_row(f"[steel_blue][link={epsteinify_url(k)}]{k}[/link][/steel_blue]", str(v))

    console.print('\n', counts_table)


def print_top_lines(file_text, n = 10, max_chars = MAX_PREVIEW_CHARS, in_panel = False):
    "Print first n lines of a file."
    file_text = LEADING_WHITESPACE_REGEX.sub('', file_text)
    top_text = escape('\n'.join(file_text.split("\n")[0:n])[0:max_chars])
    output = Panel(top_text, expand=False) if in_panel else top_text + '\n'
    console.print(output, style='dim')


if deep_debug:
    console.print('KNOWN_IMESSAGE_FILE_IDS\n--------------')
    console.print(json.dumps(KNOWN_IMESSAGE_FILE_IDS))
    console.print('\n\n\nGUESSED_IMESSAGE_FILE_IDS\n--------------')
    console.print_json(json.dumps(GUESSED_IMESSAGE_FILE_IDS))
    console.line(2)
