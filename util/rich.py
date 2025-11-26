import json
import logging
import re
import urllib.parse
from os import environ

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

LEADING_WHITESPACE_REGEX = re.compile(r'\A\s*', re.MULTILINE)
MAX_PREVIEW_CHARS = 300
OUTPUT_WIDTH = 120

ARAB_COLOR = 'dark_green'
ARCHIVE_LINK = 'archive_link'
ARCHIVE_LINK_COLOR = 'blue3'
BITCOIN_COLOR = 'orange1 bold'
CHINA_COLOR = 'bright_red'
ISRAELI_COLOR = 'dodger_blue2'
JOURNALIST_COLOR = 'grey54'
PHONE_NUMBER = 'phone_number'
RUSSIA_COLOR = 'dark_red dim'
TEXT_LINK = 'text_link'
TIMESTAMP = 'timestamp'

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

NAMES_TO_NOT_COLOR = [name.lower() for name in [
    'Black',
    'Daniel',
    'Darren',
    'David',
    'jeffrey',
    'Jr',
    'JR.',
    'Le',
    'Martin',
    'Melanie',
    'Michael',
    'Pen',
    'Peter',
    'Richard',
    'Robert',
    'Roger',
    'Steve',
    'Stone',
    'The',
    'Victor',
    "Y",
    "Y.",
]]

# Color different counterparties differently
COUNTERPARTY_COLORS = {
    ANIL: 'dark_green',
    ARIANE_DE_ROTHSCHILD: 'indian_red',
    'Celina Dubin': 'medium_orchid1',
    DEFAULT: 'wheat4',
    DONALD_TRUMP: 'red3 bold',
    JEFFREY_EPSTEIN: 'blue',
    EVA: 'orchid',
    'jeffrey wernick': BITCOIN_COLOR,
    LARRY_SUMMERS: 'spring_green4',
    MELANIE_WALKER: 'deep_pink4',
    MELANIE_SPINELLA: 'magenta3',
    MIROSLAV: 'slate_blue3',
    "Michael Wolff": JOURNALIST_COLOR,
    'Noam Chomsky': 'grey23',
    PAUL_KRASSNER: JOURNALIST_COLOR,
    PLASKETT: 'medium_orchid3',
    ROBERT_TRIVERS: 'blue_violet',
    SCARAMUCCI: 'orange1',
    SOON_YI: 'hot_pink',
    STEVE_BANNON: 'color(58)',
    TERJE: 'light_slate_blue',
    UNKNOWN: 'cyan',
}

PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED = {
    None: 'grey74',
    JEREMY_RUBIN: BITCOIN_COLOR,
    JOI_ITO: 'blue_violet',
    AL_SECKEL: 'orange_red1',
    JABOR_Y: f"{ARAB_COLOR} bold",
    DANIEL_SIAD: 'dark_khaki',
    JEAN_LUC_BRUNEL: 'wheat4',
    EHUD_BARAK: ISRAELI_COLOR,
    MARTIN_NOWAK: 'navy_blue',
    'Masha Drokova': 'deep_pink2',
    'Peter Thiel': 'orange4',
    STEVE_BANNON: COUNTERPARTY_COLORS[STEVE_BANNON],
    DAVID_STERN: 'medium_purple3',
    # Temporary
    # 'Reid Weingarten': 'magenta',
    # 'Kathy Ruemmler': 'magenta',
}

PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES = {
    GHISLAINE_MAXWELL: 'deep_pink3',
    LEON_BLACK: 'dark_cyan',
    LANDON_THOMAS: 'misty_rose3',  # FT journo
    SULTAN_BIN_SULAYEM: 'green1',
    # Epstein's lawyers
    DARREN_INDYKE: 'purple3',
    'Richard Kahn': 'purple4',
    'Deepak Chopra': 'dark_goldenrod',
}

OTHER_STYLES = {
    ARCHIVE_LINK: 'deep_sky_blue4',
    PHONE_NUMBER: 'bright_green',
    TEXT_LINK: 'deep_sky_blue4 underline',
    TIMESTAMP: 'gray30',
}

COUNTERPARTY_COLORS.update(PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED)
COUNTERPARTY_COLORS.update(PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES)
COUNTERPARTY_COLORS.update(OTHER_STYLES)
COURIER_NEWSROOM_ARCHIVE = 'https://journaliststudio.google.com/pinpoint/search?collection=092314e384a58618'
COFFEEZILLA_ARCHIVE = 'https://journaliststudio.google.com/pinpoint/search?collection=061ce61c9e70bdfd'
SUBSTACK_URL = 'https://cryptadamus.substack.com/p/i-made-epsteins-text-messages-great'
EPSTEINIFY_URL = 'https://epsteinify.com'

epsteinify_url = lambda name: f"{EPSTEINIFY_URL}/?name={urllib.parse.quote(name)}"
epsteinify_api_url = lambda file_id: f"{EPSTEINIFY_URL}/api/documents/HOUSE_OVERSIGHT_{file_id}"
epsteinify_doc_url = lambda file_stem: f"{EPSTEINIFY_URL}/document/{file_stem}"
jmail_search_url = lambda txt: f"https://jmail.world/search?q={urllib.parse.quote(txt)}"
search_archive_url = lambda txt: f"{COURIER_NEWSROOM_ARCHIVE}&q={urllib.parse.quote(txt)}&p=1"
search_coffeezilla_url = lambda txt: f"{COFFEEZILLA_ARCHIVE}&q={urllib.parse.quote(txt)}&p=1"

# Setup logging
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
    'CCP': CHINA_COLOR,
    'China': CHINA_COLOR,
    'Chinese': CHINA_COLOR,
    'Clinton': 'sky_blue1',
    'Dershowitz': 'medium_purple2',
    'DJT': COUNTERPARTY_COLORS[DONALD_TRUMP],
    'ehbarak': COUNTERPARTY_COLORS[EHUD_BARAK],
    'GMAX': COUNTERPARTY_COLORS[GHISLAINE_MAXWELL],
    'gmax1@ellmax.com': COUNTERPARTY_COLORS[GHISLAINE_MAXWELL],
    'Harvard': 'red',
    'Ivanka': 'medium_violet_red',
    'Joichi Ito': COUNTERPARTY_COLORS[JOI_ITO],
    'Jabor': COUNTERPARTY_COLORS[JABOR_Y],
    'Jared Kushner': 'medium_violet_red',
    'jeevacation@gmail.com': COUNTERPARTY_COLORS[JEFFREY_EPSTEIN],
    'kwok': CHINA_COLOR,
    'Lavrov': RUSSIA_COLOR,
    'Le Pen': 'purple4',
    'LePen': 'purple4',
    'Manafort': COUNTERPARTY_COLORS[STEVE_BANNON],
    'Miro': COUNTERPARTY_COLORS[MIROSLAV],
    'Moscow': RUSSIA_COLOR,
    'Obama': 'yellow',
    'Putin': 'dark_red bold',
    'Roger Stone': COUNTERPARTY_COLORS[DONALD_TRUMP],
    'Russia': RUSSIA_COLOR,
    'Russian': RUSSIA_COLOR,
    'Scaramucci': COUNTERPARTY_COLORS[SCARAMUCCI],
    'Victor Orban': 'purple4',
    'xi': f"{CHINA_COLOR} bold",
})

HIGHLIGHT_REGEXES = {
    re.compile(r'\b(Abu Dhabi|Dubai|Emir(ates)?|Erdogan|HBJ|Iran(ian)?|Iraq|Islam(ic|ist)?|Kaz(akh|ich)stan|Kazakh?|KSA|MB(S|Z)|Muslim|Sharia|Syria|Turkey|UAE|((Kuwait|Qatar|Saud|Yemen)i?))s?\b', re.I): ARAB_COLOR,
    re.compile(r'\b(bitcoin|coins|cr[iy]pto(currency)?|e-currency|(Howard\s+)?Lutnick|Tether)\b', re.I): BITCOIN_COLOR,
    re.compile(r'\b(Bibi|ehbarak|Netanyahu|Israeli?)\b', re.I): ISRAELI_COLOR,
    re.compile(r'\b(Bra[sz]il(ian)?|Bolsonar[aio]|Lula)\b', re.I): 'chartreuse2',
}


def make_link_markup(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> str:
    return f"[underline][bold][{style}][link={url}]{link_text}[/link][/{style}][/bold][/underline]"


def make_link(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(make_link_markup(url, link_text, style))


def archive_link(filename: str, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
    return make_link(search_archive_url(filename), link_txt or filename, style)


def coffeezilla_link(search_term: str, link_txt: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return make_link(search_archive_url(search_term), link_txt or search_term, style)


def highlight_names(text: str) -> str:
    for name_regex, style in HIGHLIGHT_REGEXES.items():
        text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

    for name, style in COUNTERPARTY_COLORS.items():
        if name is None or name == DEFAULT:
            continue

        name_regex = re.compile(rf"\b({name}s?)\b", re.IGNORECASE)
        text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

        if ' ' not in name:
            continue

        names = name.split(' ')
        last_name = names[-1]
        first_name = ' '.join(names[0:-1])

        # highlight last names
        if last_name.lower() not in NAMES_TO_NOT_COLOR:
            name_regex = re.compile(rf"(?!{first_name} ?)\b({last_name}s?)\b", re.IGNORECASE)
            text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

        # highlight first names
        if len(first_name) > 2 and first_name.lower() not in NAMES_TO_NOT_COLOR:
            name_regex = re.compile(rf"\b({first_name}s?)\b(?! ?{last_name})", re.IGNORECASE)
            text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

    return text


def print_header():
    console.print(f"This site is not optimized for mobile but if you get past the header it should work ok.", style='dim')
    console.line()
    console.print(Panel(Text("Epstein Estate Documents - Seventh Production Collection Reformatted Text Messages", justify='center', style='bold reverse')))
    console.line()
    console.print(Align.center(f"[bold][link={SUBSTACK_URL}]I Made Epstein's Text Messages Great Again (And You Should Read Them)[/link][/bold]"))
    console.print(Align.center(f"[blue][underline][link={SUBSTACK_URL}]{SUBSTACK_URL.removeprefix('https://')}[/link][/underline][/blue]"))
    console.print(Align.center("[link=https://cryptadamus.substack.com/]Substack[/link]"))
    console.print(Align.center("[link=https://universeodon.com/@cryptadamist]Mastodon[/link]"))
    console.print(Align.center("[link=https://x.com/Cryptadamist/status/1990866804630036988]Twitter[/link]"))
    # Acronym table
    table = Table(title="Abbreviations Used Frequently In These Chats", show_header=True, header_style="bold")
    table.add_column("Abbreviation", justify="center", style='bold', width=19)
    table.add_column("Translation", style="deep_sky_blue4", justify="center")

    for k, v in ABBREVIATIONS.items():
        table.add_row(highlight_names(k), v)

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
    console.print(Align.center("[link=https://github.com/michelcrypt4d4mus/epstein_text_messages/blob/master/util/constants.py]Explanation of attributions[/link]"), style='magenta')
    console.line(2)


def print_email_table(counts: dict[str, int], column_title: str) -> None:
    counts_table = Table(title=f"Email Counts By {column_title}", show_header=True, header_style="bold")
    counts_table.add_column(column_title, justify="left")
    counts_table.add_column("Email Count", justify="center")

    for k, v in sorted(counts.items(), key=lambda item: item[0] if 'ALPHA' in environ else [item[1], item[0]], reverse=True):
        k = k.title() if ' ' in k else k
        style = COUNTERPARTY_COLORS.get(k, 'white').replace('bold', '').strip()
        name_txt = Text.from_markup(f"[{style}][link={epsteinify_url(k)}]{k}[/link][/{style}]")
        counts_table.add_row(name_txt, str(v))

    console.print('\n', counts_table)


def print_section_header(msg: str, style: str = 'bold white on blue3', is_centered: bool = True) -> None:
    panel = Panel(Text(msg, justify='center'), width=80, padding=(1, 1), style=style)

    if is_centered:
        panel = Align.center(panel)

    console.print(panel)
    console.line()


def print_top_lines(file_text, n = 10, max_chars = MAX_PREVIEW_CHARS, in_panel = False):
    """Print first n lines of a file."""
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
