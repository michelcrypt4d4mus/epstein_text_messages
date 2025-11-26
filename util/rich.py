import json
import logging
import re
from os import environ

from rich.align import Align
from rich.console import Console
from rich.logging import RichHandler
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.terminal_theme import TerminalTheme
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
BRASIL_COLOR = 'chartreuse2'
CHINA_COLOR = 'bright_red'
DEMS_COLOR = 'sky_blue1'
HEADER_LINK = 'deep_sky_blue1'
INDIA_COLOR = 'green'
ISRAELI_COLOR = 'dodger_blue2'
JAVANKA_COLOR = 'medium_violet_red'
JOURNALIST_COLOR = 'grey54'
OBAMA_COLOR = 'yellow'
PHONE_NUMBER = 'phone_number'
RUSSIA_COLOR = 'dark_red'
TEXT_LINK = 'text_link'
TIMESTAMP = 'timestamp'
TRUMP_COLOR = 'red3 bold'

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
    'Paul',
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
    ANIL: INDIA_COLOR,
    ARIANE_DE_ROTHSCHILD: 'indian_red',
    'Celina Dubin': 'medium_orchid1',
    DEFAULT: 'wheat4',
    JEFFREY_EPSTEIN: 'blue1',
    EVA: 'orchid',
    'jeffrey wernick': BITCOIN_COLOR,
    LARRY_SUMMERS: 'spring_green4',
    MELANIE_SPINELLA: 'magenta3',
    MELANIE_WALKER: 'deep_pink4',
    MICHAEL_WOLFF: JOURNALIST_COLOR,
    MIROSLAV: 'slate_blue3',
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
    MARTIN_NOWAK: 'dark_turquoise',
    'Masha Drokova': RUSSIA_COLOR,
    'Peter Thiel': 'orange4',
    STEVE_BANNON: COUNTERPARTY_COLORS[STEVE_BANNON],
    DAVID_STERN: 'medium_purple3',
    MOHAMED_WAHEED_HASSAN: ARAB_COLOR,
    PAULA: 'pink1',
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

HIGHLIGHT_PATTERNS: dict[str, str] = {
    ARAB_COLOR: r"Abu\s+Dhabi|Assad|Dubai|Emir(ates)?|Erdogan|Gaddafi|HBJ|Iran(ian)?|Islam(ic|ist)?|Istanbul|Kh?ashoggi|Kaz(akh|ich)stan|Kazakh?|KSA|MB(S|Z)|Mohammed\s+bin\s+Salman|Muslim|Saudi(\s+Arabian?)?|Sharia|Syria|Turkey|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
    BITCOIN_COLOR: r"bitcoin|block ?chain( capital)?|coins|cr[iy]pto(currency)?|e-currency|(Howard\s+)?Lutnick|Libra|Tether|(zero\s+knowledge\s+|zk)pro(of|tocols?)",
    BRASIL_COLOR: r"Bra[sz]il(ian)?|Bolsonar[aio]|Lula",
    CHINA_COLOR: r"CCP|Chin(a|ese)|Guo|Kwok|Tai(pei|wan)|PRC|xi",
    DEMS_COLOR: r"Maxine Waters|(Nancy )?Pelosi|Clinton|Hillary",
    INDIA_COLOR: r"Ambani|Indian?|Modi|mumbai",
    ISRAELI_COLOR: r"Bibi|ehbarak|Netanyahu|Israeli?",
    RUSSIA_COLOR: r"Moscow|(Vladimir )?Putin|Lavrov|Russian?",
    TRUMP_COLOR: r"(Donald\s+(J\.\s+)?)?Trump|Donald|DJT|Roger\s+Stone",
    COUNTERPARTY_COLORS[GHISLAINE_MAXWELL]: r"GMAX|gmax1@ellmax.com",
    'dark_cyan': r"(Steve\s+)?Wynn|(Leslie\s+)?Wexner",
    'dark_magenta': r"Le\s*Pen|(Victor\s+)?Orbah?n",
    'orchid1': r"(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre|Virginia\s+Roberts",
    'medium_purple2': r"(Alan (M\. )?)?Dershowi(l|tz)|(Ken(neth W.)?\s+)?Starr",
    'pale_green1': r"Masa(yoshi)?|Najeev|Softbank",
    'turquoise4': r"BG|Bill\s+((and|or)\s+Melinda\s+)?Gates|Melinda(\s+Gates)?",
}

# Wrap in \b, add optional s? at end of all regex patterns
HIGHLIGHT_REGEXES: dict[str, re.Pattern] = {k: re.compile(fr"\b(({v})s?)\b", re.I) for k, v in HIGHLIGHT_PATTERNS.items()}

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

# Swap black for white
HTML_TERMINAL_THEME = TerminalTheme(
    (0, 0, 0),
    (255, 255, 255),
    [
        (0, 0, 0),
        (128, 0, 0),
        (0, 128, 0),
        (128, 128, 0),
        (0, 0, 128),
        (128, 0, 128),
        (0, 128, 128),
        (192, 192, 192),
    ],
    [
        (128, 128, 128),
        (255, 0, 0),
        (0, 255, 0),
        (255, 255, 0),
        (0, 0, 255),
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 255),
    ],
)


# Instantiate Console object
console = Console(color_system='256', theme=Theme(COUNTERPARTY_COLORS), width=OUTPUT_WIDTH)
console.record = True

# This is after the Theme() instantiation because 'bg' is reserved'
COUNTERPARTY_COLORS.update({
    'Biden': OBAMA_COLOR,
    'Harvard': 'red',
    'Ivanka': JAVANKA_COLOR,
    'Joichi Ito': COUNTERPARTY_COLORS[JOI_ITO],
    'Jabor': COUNTERPARTY_COLORS[JABOR_Y],
    'Jared Kushner': JAVANKA_COLOR,
    'jeevacation@gmail.com': COUNTERPARTY_COLORS[JEFFREY_EPSTEIN],
    'Paul Manafort': COUNTERPARTY_COLORS[STEVE_BANNON],
    'Miro': COUNTERPARTY_COLORS[MIROSLAV],
    'Obama': OBAMA_COLOR,
    'Scaramucci': COUNTERPARTY_COLORS[SCARAMUCCI],
})


# Setup logging
logging.basicConfig(level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("rich")

if deep_debug:
    logger.setLevel(logging.DEBUG)
elif is_debug:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)


def make_link_markup(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> str:
    return f"[underline][bold][{style}][link={url}]{link_text}[/link][/{style}][/bold][/underline]"


def make_link(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(make_link_markup(url, link_text, style))


def archive_link(filename: str, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
    return make_link(search_archive_url(filename), link_txt or filename, style)


def coffeezilla_link(search_term: str, link_txt: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return make_link(search_archive_url(search_term), link_txt or search_term, style)


def highlight_names(text: str) -> str:
    for style, name_regex in HIGHLIGHT_REGEXES.items():
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
    console.print(Align.center(f"[underline][link={SUBSTACK_URL}]I Made Epstein's Text Messages Great Again (And You Should Read Them)[/link][/underline]"), style=f'{HEADER_LINK} bold')
    console.print(Align.center(f"[dodger_blue3][underline][link={SUBSTACK_URL}]{SUBSTACK_URL.removeprefix('https://')}[/link][/underline][/dodger_blue3]"))
    console.print(Align.center("[underline][link=https://cryptadamus.substack.com/]Substack[/link][/underline]"), style=HEADER_LINK)
    console.print(Align.center("[underline][link=https://universeodon.com/@cryptadamist]Mastodon[/link][/underline]"), style=HEADER_LINK)
    console.print(Align.center("[underline][link=https://x.com/Cryptadamist/status/1990866804630036988]Twitter[/link][/underline]"), style=HEADER_LINK)
    # Acronym table
    table = Table(title="Abbreviations Used Frequently In These Chats", show_header=True, header_style="bold")
    table.add_column("Abbreviation", justify="center", style='bold', width=19)
    table.add_column("Translation", style="white", justify="center")

    for k, v in HEADER_ABBREVIATIONS.items():
        table.add_row(highlight_names(k), v)

    console.line()
    console.print(Align.center(table))
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


def print_email_table(counts: dict[str, int], column_title: str) -> None:
    counts_table = Table(title=f"Email Counts By {column_title}", show_header=True, header_style="bold")
    counts_table.add_column(column_title, justify="left", style='white')
    counts_table.add_column("Email Count", justify="center")

    for k, v in sorted(counts.items(), key=lambda item: item[0] if 'ALPHA' in environ else [item[1], item[0]], reverse=True):
        k = k.title() if ' ' in k else k
        name_txt = Text.from_markup(f"[underline][link={epsteinify_name_url(k)}]{highlight_names(k)}[/link][/underline]")
        counts_table.add_row(name_txt, str(v))

    console.print(counts_table)


def print_section_header(msg: str, style: str = 'bold white on blue3', is_centered: bool = True) -> None:
    panel = Panel(Text(msg, justify='center'), width=80, padding=(1, 1), style=style)

    if is_centered:
        panel = Align.center(panel)

    console.print(panel)
    console.line()


def print_panel(msg: str, style: str = 'black on white') -> None:
    console.print(Panel(Text(msg, justify='center'), width=70, style=style), '\n')


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
