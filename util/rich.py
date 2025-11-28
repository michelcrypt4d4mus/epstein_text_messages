import json
import re
from os import devnull

from rich.align import Align
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .constants import *
from .data import flatten
from .env import args, deep_debug, is_build, logger
from .strings import regex_escape_periods
from .text_highlighter import EpsteinTextHighlighter

ALL_EMAILS_URL = 'https://michelcrypt4d4mus.github.io/epstein_emails_house_oversight/'
LEADING_WHITESPACE_REGEX = re.compile(r'\A\s*', re.MULTILINE)
NON_ALPHA_CHARS_REGEX = re.compile(r'[^a-zA-Z0-9 ]')
MAX_PREVIEW_CHARS = 300
OUTPUT_WIDTH = 120
HEADER_STYLE = 'header_field'
PHONE_NUMBER = 'phone_number'
SENT_FROM = 'sent_from'
TEXT_LINK = 'text_link'
TIMESTAMP = 'timestamp'
SECTION_HEADER_STYLE = 'bold white on blue3'

highlighter_style_name = lambda style_name: f"{HEADER_FIELD}.{style_name}"

ARAB_COLOR = 'dark_sea_green4'
ARCHIVE_LINK = 'archive_link'
ARCHIVE_LINK_COLOR = 'blue3'
BANK_COLOR = 'bright_green' # 'green
BITCOIN_COLOR = 'orange1 bold'
BRASIL_COLOR = 'chartreuse2'
BRO_COLOR = 'tan'
CHINA_COLOR = 'bright_red'
COLLEGE_COLOR = 'deep_pink2'
DEMS_COLOR = 'sky_blue1'
DUBIN_COLOR = 'medium_orchid1'
HEADER_LINK = 'deep_sky_blue1'
HEADER_COLOR = 'light_sea_green'
INDIA_COLOR = 'green'
ISRAELI_COLOR = 'dodger_blue2'
JAVANKA_COLOR = 'medium_violet_red'
JOURNALIST_COLOR = 'yellow3'
LAWYER_COLOR = 'purple3'
LOBBYIST_COLOR = 'medium_purple'
OBAMA_COLOR = 'yellow'
POLICE_COLOR = 'color(24)'
RICH_GUY_COLOR = 'dark_cyan'
RUSSIA_COLOR = 'red bold'
SCHOLAR_COLOR = 'light_goldenrod2'
TECH_BRO_COLOR = 'orange4'
TRUMP_COLOR = 'red3 bold'

BASE_NAMES_TO_NOT_COLOR: list[str] = [name.lower() for name in [
    'Allen',
    'Andrew',
    'Black',
    'Daniel',
    'Darren',
    'David',
    'jeffrey',
    'John',
    'Jonathan',
    'Joseph',
    'Kahn',
    'Jr',
    'JR.',
    'Le',
    'Leon',
    'Marc',
    'Martin',
    'Melanie',
    'Michael',
    'Paul',
    'Pen',
    'Peter',
    'Reid',
    'Richard',
    'Robert',
    'Roger',
    'Rubin',
    'Scott',
    'Stephen',
    'Steve',
    'Steven',
    'Stone',
    'Susan',
    'The',
    'Thomas',
    'Tom',
    'Victor',
    "Y",
    "Y.",
]]

NAMES_TO_NOT_COLOR = [[n, regex_escape_periods(n)] if '.' in n else [n] for n in BASE_NAMES_TO_NOT_COLOR]
NAMES_TO_NOT_COLOR = flatten(NAMES_TO_NOT_COLOR)

# Color different counterparties differently
COUNTERPARTY_COLORS = {
    ALIREZA_ITTIHADIEH: ARAB_COLOR,  # Iranian / British?
    ANIL: INDIA_COLOR,
    BRAD_KARP: LAWYER_COLOR,
    CELINA_DUBIN: DUBIN_COLOR,
    DAVID_SCHOEN: LAWYER_COLOR,
    DAVID_HAIG: SCHOLAR_COLOR,
    DEFAULT: 'wheat4',
    EVA: 'orchid',
    'Eva Dubin': DUBIN_COLOR,
    GLENN_DUBIN: DUBIN_COLOR,
    JAY_LEFKOWITZ: LAWYER_COLOR,
    JEFFREY_EPSTEIN: 'blue1',
    JONATHAN_FARKAS: BRO_COLOR,
    JOSCHA_BACH: SCHOLAR_COLOR,
    LARRY_SUMMERS: SCHOLAR_COLOR,
    LINDA_STONE: 'pink3',
    LILLY_SANCHEZ: LAWYER_COLOR,
    MARTIN_WEINBERG: LAWYER_COLOR,
    MELANIE_SPINELLA: 'magenta3',
    MELANIE_WALKER: 'light_pink3',
    NADIA_MARCINKO: 'violet',
    MIROSLAV: 'slate_blue3',
    'Moshe Hoffman': SCHOLAR_COLOR,
    'Noam Chomsky': SCHOLAR_COLOR,
    PAUL_MORRIS: BANK_COLOR,
    REID_WEINGARTEN: LAWYER_COLOR,
    'Rob Crowe': LOBBYIST_COLOR,
    ROBERT_TRIVERS: SCHOLAR_COLOR,
    'Roy Black': LAWYER_COLOR,
    SCARAMUCCI: 'orange1',
    SCOTT_J_LINK: LAWYER_COLOR,
    SOON_YI: 'hot_pink',
    STACY_PLASKETT: 'medium_orchid3',
    STEVE_BANNON: 'color(58)',
    TERJE: 'light_slate_blue',
    TOM_BARRACK: BRO_COLOR,
    UNKNOWN: 'cyan',
    'Woody Allen': 'light_steel_blue3',
}

PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED = {
    JEREMY_RUBIN: BITCOIN_COLOR,
    JOI_ITO: 'blue_violet',
    AL_SECKEL: 'orange_red1',
    JABOR_Y: "spring_green1",
    DANIEL_SIAD: 'dark_khaki',
    JEAN_LUC_BRUNEL: 'wheat4',
    EHUD_BARAK: ISRAELI_COLOR,
    MARTIN_NOWAK: COLLEGE_COLOR,  # Really harvard color...
    'Masha Drokova': RUSSIA_COLOR,
    OLIVIER_COLOM: LOBBYIST_COLOR,
    'Peter Thiel': TECH_BRO_COLOR,
    STEVE_BANNON: COUNTERPARTY_COLORS[STEVE_BANNON],
    DAVID_STERN: 'medium_purple3',
    MOHAMED_WAHEED_HASSAN: ARAB_COLOR,
    PAULA: 'pink1',
    REID_HOFFMAN: TECH_BRO_COLOR,
    BORIS_NIKOLIC: BRO_COLOR,
    PRINCE_ANDREW: 'dodger_blue1',
    'Jide Zeitlin': BANK_COLOR,
    ARIANE_DE_ROTHSCHILD: 'indian_red',
    None: 'grey74',
}

PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES = {
    GHISLAINE_MAXWELL: 'deep_pink3',
    LEON_BLACK: 'dark_cyan',
    LANDON_THOMAS: 'misty_rose3',  # FT journo
    SULTAN_BIN_SULAYEM: 'green1',
    # Epstein's lawyers
    DARREN_INDYKE: LAWYER_COLOR,
    RICHARD_KAHN: 'purple4',
    DEEPAK_CHOPRA: 'dark_goldenrod',
    # Temporary
    KATHY_RUEMMLER: 'magenta2',
    TYLER_SHEARS: BITCOIN_COLOR,  # PR
}

OTHER_STYLES = {
    ARCHIVE_LINK: 'deep_sky_blue4',
    PHONE_NUMBER: 'bright_green',
    TEXT_LINK: 'deep_sky_blue4 underline',
    TIMESTAMP: 'gray30',
    HEADER_STYLE: 'plum4',
    highlighter_style_name('email'): 'bright_cyan',
    SENT_FROM: 'gray50 italic dim',
}

COUNTERPARTY_COLORS.update(PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED)
COUNTERPARTY_COLORS.update(PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES)
COUNTERPARTY_COLORS.update(OTHER_STYLES)

HIGHLIGHT_PATTERNS: dict[str, str] = {
    ARAB_COLOR: rf"Abdulmalik Al-Makhlafi|Abu\s+Dhabi|{ANAS_ALRASHEED}|Assad|Dubai|Emir(ates)?|Erdogan|Gaddafi|HBJ|Imran Khan|Iran(ian)?|Islam(ic|ist)?|Istanbul|Kh?ashoggi|Kaz(akh|ich)stan|Kazakh?|KSA|MB(S|Z)|Mohammed\s+bin\s+Salman|Muslim|Pakistani?|Riya(dh|nd)|Saudi(\s+Arabian?)?|Shaher Abdulhak Besher|Sharia|Syria|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
    BITCOIN_COLOR: r"bitcoin|block ?chain( capital)?|coins|cr[iy]pto(currency)?|e-currency|(jeffrey\s+)?wernick|(Howard\s+)?Lutnick|Libra|Tether|(zero\s+knowledge\s+|zk)pro(of|tocols?)",
    BRASIL_COLOR: r"Argentina|Bra[sz]il(ian)?|Bolsonar[aio]|Lula|(Nicolas )?Maduro|Venezuelan?s?",
    CHINA_COLOR: r"Beijing|CCP|Chin(a|ese)|Guo|Kwok|Tai(pei|wan)|Peking|PRC|xi",
    COLLEGE_COLOR: rf"{LISA_NEW}|Harvard|MIT( Media Lab)?|Media Lab",
    DEMS_COLOR: r"Maxine Waters|(Nancy )?Pelosi|Clinton|Hillary",
    INDIA_COLOR: rf"Ambani|Indian?|Modi|mumbai|Zubair( Khan)?|{VINIT_SAHNI}",
    ISRAELI_COLOR: r"Bibi|(eh|Nili Priell )barak|Netanyahu|Israeli?",
    JOURNALIST_COLOR: rf"Alex Yablon|{PAUL_KRASSNER}|{MICHAEL_WOLFF}|Wolff|Susan Edelman",
    POLICE_COLOR: f"Police Code Enforcement|Ann Marie Villafana|Kirk Blouin",
    RICH_GUY_COLOR: rf"(Steve\s+)?Wynn|(Leslie\s+)?Wexner|Amanda Ens|{NICHOLAS_RIBIS}|{ROBERT_LAWRENCE_KUHN}|{STEPHEN_HANSON}|{TERRY_KAFKA}",
    RUSSIA_COLOR: r"GRU|FSB|Lavrov|Moscow|(Vladimir )?Putin|Russian?|Vladimir Yudashkin",
    TRUMP_COLOR: r"(Donald\s+(J\.\s+)?)?Trump|Donald|DJT|Roger\s+Stone",
    COUNTERPARTY_COLORS[GHISLAINE_MAXWELL]: r"GMAX|gmax1@ellmax.com",
    COUNTERPARTY_COLORS[TERJE]: r"Terje (R[øo]e?d[- ])?Lars[eo]n",
    COUNTERPARTY_COLORS[JEFFREY_EPSTEIN]: EMAILER_REGEXES[JEFFREY_EPSTEIN].pattern,
    'dark_magenta': r"Le\s*Pen|(Victor\s+)?Orbah?n",
    'orchid1': r"(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre|Virginia\s+Roberts",
    'medium_purple2': r"(Alan (M\. )?)?Dershowi(l|tz)|(Ken(neth W.)?\s+)?Starr",
    'pale_green1': r"Masa(yoshi)?|Najeev|Softbank",
    'turquoise4': r"BG|Bill\s+((and|or)\s+Melinda\s+)?Gates|Melinda(\s+Gates)?",
    BANK_COLOR: r"Black(rock|stone)|DB|Deutsche Bank|Goldman( Sachs)|Morgan Stanley|j\.?p\.? ?morgan( Chase)?|Chase Bank",
    HEADER_STYLE: r"^((Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):)"
}

# Wrap in \b, add optional s? at end of all regex patterns
HIGHLIGHT_REGEXES: dict[str, re.Pattern] = {
    # [\b\n] or no trailing \b is required for cases when last char in match is not a word char (e.g. when it's '.')
    k: re.compile(fr"\b(({v})s?)\b", re.I) if k != HEADER_STYLE else re.compile(v, re.MULTILINE)
    for k, v in HIGHLIGHT_PATTERNS.items()
}

# Instantiate console object
CONSOLE_ARGS = {
    'color_system': '256',
    'highlighter': EpsteinTextHighlighter(),
    'record': True,
    'theme': Theme(COUNTERPARTY_COLORS),
    'width': OUTPUT_WIDTH,
}

if is_build:
    print(f"Suppressing console output because is_build={is_build}...")
    CONSOLE_ARGS.update({'file': open(devnull, "wt")})

console = Console(**CONSOLE_ARGS)


# This is after the Theme() instantiation because 'bg' is reserved'
COUNTERPARTY_COLORS.update({
    'Biden': OBAMA_COLOR,
    'Ivanka': JAVANKA_COLOR,
    'Joichi Ito': COUNTERPARTY_COLORS[JOI_ITO],
    'Jared Kushner': JAVANKA_COLOR,
    'jeevacation@gmail.com': COUNTERPARTY_COLORS[JEFFREY_EPSTEIN],
    'Paul Manafort': COUNTERPARTY_COLORS[STEVE_BANNON],
    'Miro': COUNTERPARTY_COLORS[MIROSLAV],
    'Obama': OBAMA_COLOR,
    'Scaramucci': COUNTERPARTY_COLORS[SCARAMUCCI],
})


def make_link_markup(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> str:
    return f"[underline][bold][{style}][link={url}]{link_text}[/link][/{style}][/bold][/underline]"


def make_link(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(make_link_markup(url, link_text, style))


def archive_link(filename: str, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
    return make_link(search_archive_url(filename), link_txt or filename, style)


def coffeezilla_link(search_term: str, link_txt: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return make_link(search_archive_url(search_term), link_txt or search_term, style)


def get_style_for_name(name: str) -> str:
    if name in COUNTERPARTY_COLORS:
        return COUNTERPARTY_COLORS[name]

    for style, name_regex in HIGHLIGHT_REGEXES.items():
        if name_regex.search(name):
            return style

    return DEFAULT


def highlight_text(text: str) -> str:
    for style, name_regex in HIGHLIGHT_REGEXES.items():
        text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

    for name, style in COUNTERPARTY_COLORS.items():
        if name in [None, DEFAULT, HEADER_STYLE, SENT_FROM]:
            continue

        name = regex_escape_periods(name)
        name_regex = re.compile(rf"\b({name}s?)\b", re.IGNORECASE)
        text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

        if ' ' not in name:
            continue

        names = name.split(' ')
        last_name = names[-1]
        first_name = ' '.join(names[0:-1])

        # TODO: ugly handling for "Jabor You" case
        if 'jabor' == first_name.lower():
            name_regex = re.compile(rf"\b(jabors?)\b", re.IGNORECASE)
            text = name_regex.sub(rf'[{style}]\1[/{style}]', text)
            continue

        # highlight last names
        if last_name.lower() not in NAMES_TO_NOT_COLOR:
            name_regex = re.compile(rf"(?!{first_name} ?)\b({last_name}s?)\b", re.IGNORECASE)
            text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

        # highlight first names
        if len(first_name) > 2 and first_name.lower() not in NAMES_TO_NOT_COLOR:
            name_regex = re.compile(rf"\b({first_name}s?)\b(?! ?{last_name})", re.IGNORECASE)
            text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

    return text


def highlight_pattern(text: str, pattern: re.Pattern, style: str = 'cyan') -> Text:
    return Text.from_markup(pattern.sub(rf'[{style}]\1[/{style}]', text))


def print_all_emails_link() -> None:
    console.print(
        Align.center(f"[underline][link={ALL_EMAILS_URL}]Another site made by this code where you can read ALL of His Emails[/link][/underline]"),
        style=f'chartreuse3 bold'
    )


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
    console.line()
    print_all_emails_link()

    # Acronym table
    table = Table(title="Abbreviations Used Frequently In These Chats", show_header=True, header_style="bold")
    table.add_column("Abbreviation", justify="center", style='bold', width=19)
    table.add_column("Translation", style="white", justify="center")

    for k, v in HEADER_ABBREVIATIONS.items():
        table.add_row(highlight_text(k), v)

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
    console.print(Align.center("(thanks to [dodger_blue3][link=https://x.com/ImDrinknWyn]@ImDrinknWyn[/link][/dodger_blue3] and others for attribution help)"))
    console.print(Align.center("[link=https://github.com/michelcrypt4d4mus/epstein_text_messages/blob/master/util/constants.py]Explanation of attributions[/link]"), style='magenta')


def print_emailer_counts_table(counts: dict[str, int], column_title: str) -> None:
    counts_table = Table(title=f"Email Counts by {column_title}", show_header=True, header_style="bold")
    counts_table.add_column(column_title, justify="left", style='white')
    counts_table.add_column('Jmail', justify="center")
    counts_table.add_column("Email Count", justify="center")

    for k, v in sorted(counts.items(), key=lambda item: item[0] if args.sort_alphabetical else [item[1], item[0]], reverse=True):
        k = k if ' ' in k else k
        name_txt = Text.from_markup(f"[underline][link={epsteinify_name_url(k)}]{highlight_text(k)}[/link][/underline]")
        jmail_link = make_link(jmail_search_url(k), 'Search Jmail')
        counts_table.add_row(name_txt, jmail_link, str(v))

    console.print(counts_table)


def print_author_header(msg: str, color: str | None) -> None:
    txt = Text(msg, justify='center')
    color = 'white' if color == DEFAULT else (color or 'white')
    panel = Panel(txt, width=80, style=f"black on {color or 'white'} bold")
    console.print('\n', Align.center(panel), '\n')


def print_numbered_list(_list: list[str] | dict) -> None:
    for i, name in enumerate(_list):
        name = name or UNKNOWN
        console.print(Text(f"   {i}. ").append(name, style=get_style_for_name(name)))


def print_section_header(msg: str, style: str = SECTION_HEADER_STYLE, is_centered: bool = False) -> None:
    panel = Panel(Text(msg, justify='center'), expand=True, padding=(1, 1), style=style)

    if is_centered:
        panel = Align.center(panel)

    console.print(panel)
    console.line()


def print_panel(msg: str, style: str = 'black on white', padding: tuple = (0, 0, 0, 0)) -> None:
    console.print(Padding(Panel(Text.from_markup(msg, justify='center'), width=70, style=style), padding))
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
