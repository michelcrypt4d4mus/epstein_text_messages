# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
import json
import re
from os import devnull

from rich.align import Align
from rich.console import Console, RenderResult
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .constants import *
from .data import flatten
from .env import args, deep_debug, logger
from .strings import regex_escape_periods
from .text_highlighter import EpsteinTextHighlighter

ALL_EMAILS_URL = 'https://michelcrypt4d4mus.github.io/epstein_emails_house_oversight/'
TEXT_MSGS_URL = 'https://michelcrypt4d4mus.github.io/epstein_text_messages/'
LEADING_WHITESPACE_REGEX = re.compile(r'\A\s*', re.MULTILINE)
NON_ALPHA_CHARS_REGEX = re.compile(r'[^a-zA-Z0-9 ]')
VERTICAL_PADDING = (1, 0, 1, 0)
MAX_PREVIEW_CHARS = 300
OUTPUT_WIDTH = 120
NUM_COLOR_KEY_COLS = 3
ARCHIVE_LINK = 'archive_link'
COLOR_SUFFIX = '_COLOR'
HEADER_STYLE = 'header_field'
PHONE_NUMBER = 'phone_number'
SENT_FROM = 'sent_from'
TEXT_LINK = 'text_link'
TIMESTAMP = 'timestamp'
SECTION_HEADER_STYLE = 'bold white on blue3'

highlighter_style_name = lambda style_name: f"{HEADER_FIELD}.{style_name}"

# Constant variables that end in "_COLOR" will be scanned to create the color highlight guide table.
ARCHIVE_LINK_COLOR = 'blue3'
BANK_COLOR = 'green'
BANNON_COLOR = 'color(58)'
BITCOIN_COLOR = 'orange1 bold'
BUSINESS_COLOR = 'spring_green4'
BRO_COLOR = 'tan'
CHINA_COLOR = 'bright_red'
DEFAULT_NAME_COLOR = 'grey82'
DEMOCRATS_COLOR = 'sky_blue1'
DUBIN_COLOR = 'medium_orchid1'
ELON_COLOR = 'light_goldenrod3'
ENTERTAINERS_COLOR = 'light_steel_blue3'
EUROPEAN_COLOR = 'dark_magenta'
HARVARD_COLOR = 'deep_pink2'
HEADER_LINK = 'deep_sky_blue1'
INDIA_COLOR = 'bright_green'
ISRAEL_COLOR = 'dodger_blue2'
JAVANKA_COLOR = 'medium_violet_red'
JOURNALIST_COLOR = 'navajo_white3'
LAWYER_COLOR = 'medium_purple2'
LOBBYIST_COLOR = 'light_coral'
MIDDLE_EAST_COLOR = 'dark_sea_green4'
POLICE_COLOR = 'color(24)'
RUSSIA_COLOR = 'red bold'
SCHOLAR_COLOR = 'light_goldenrod2'
SOUTH_AMERICA_COLOR = 'yellow'
TECH_BRO_COLOR = 'orange4'
TRUMP_COLOR = 'red3 bold'
VC_COLOR = 'pale_green1'

BASE_NAMES_TO_NOT_HIGHLIGHT: list[str] = [name.lower() for name in [
    'Allen',
    'Amanda',
    'Andres',
    'Andrew',
    'Black',
    'Brad',
    'Daniel',
    'Darren',
    'David',
    'Etienne',
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
    'Sean',
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

NAMES_TO_NOT_HIGHLIGHT = [[n, regex_escape_periods(n)] if '.' in n else [n] for n in BASE_NAMES_TO_NOT_HIGHLIGHT]
NAMES_TO_NOT_HIGHLIGHT = flatten(NAMES_TO_NOT_HIGHLIGHT)

# Color different counterparties differently
COUNTERPARTY_COLORS = {
    ALIREZA_ITTIHADIEH: MIDDLE_EAST_COLOR,  # Iranian / British?
    'Amanda Ens': BANK_COLOR,
    ANIL: INDIA_COLOR,
    BRAD_KARP: LAWYER_COLOR,
    CELINA_DUBIN: DUBIN_COLOR,
    DEFAULT: 'wheat4',
    'Elon Musk': ELON_COLOR,
    EVA: 'orchid',
    'Eva Dubin': DUBIN_COLOR,
    GLENN_DUBIN: DUBIN_COLOR,
    JEFFREY_EPSTEIN: 'blue1',
    JONATHAN_FARKAS: BRO_COLOR,
    LARRY_SUMMERS: HARVARD_COLOR,
    LINDA_STONE: 'pink3',
    MELANIE_SPINELLA: 'magenta3',
    MELANIE_WALKER: 'light_pink3',
    NADIA_MARCINKO: 'hot_pink',
    MIROSLAV: EUROPEAN_COLOR,
    PAUL_MORRIS: BANK_COLOR,
    'Rob Crowe': LOBBYIST_COLOR,
    SCARAMUCCI: BITCOIN_COLOR.removesuffix(' bold'),
    SOON_YI: 'hot_pink',
    STACY_PLASKETT: 'medium_orchid3',
    'Stanley Rosenberg': LOBBYIST_COLOR,  # Former state senator?
    SEAN_BANNON: BANNON_COLOR,
    STEVE_BANNON: BANNON_COLOR,
    TERJE: 'light_slate_blue',
    TOM_BARRACK: BRO_COLOR,
    UNKNOWN: 'cyan',
}

# ORder matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED = {
    JEREMY_RUBIN: BITCOIN_COLOR,
    JOI_ITO: 'blue_violet',
    AL_SECKEL: 'orange_red1',
    JABOR_Y: "spring_green1",
    DANIEL_SIAD: 'dark_khaki',
    JEAN_LUC_BRUNEL: 'wheat4',
    EHUD_BARAK: ISRAEL_COLOR,
    MARTIN_NOWAK: HARVARD_COLOR,  # TODO: Really harvard color...
    'Masha Drokova': RUSSIA_COLOR,
    OLIVIER_COLOM: LOBBYIST_COLOR,
    'Peter Thiel': TECH_BRO_COLOR,
    STEVE_BANNON: COUNTERPARTY_COLORS[STEVE_BANNON],
    DAVID_STERN: LAWYER_COLOR,
    MOHAMED_WAHEED_HASSAN: MIDDLE_EAST_COLOR,
    PAULA: 'pink1',
    REID_HOFFMAN: TECH_BRO_COLOR,
    BORIS_NIKOLIC: BRO_COLOR,
    PRINCE_ANDREW: 'dodger_blue1',
    'Jide Zeitlin': BANK_COLOR,
    ARIANE_DE_ROTHSCHILD: 'indian_red',
    None: 'grey74',
}

# ORder matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES = {
    GHISLAINE_MAXWELL: 'deep_pink3',
    LEON_BLACK: 'dark_cyan',
    LANDON_THOMAS: 'misty_rose3',  # FT journo
    SULTAN_BIN_SULAYEM: 'green1',
    # Epstein's lawyers
    DARREN_INDYKE: LAWYER_COLOR,
    RICHARD_KAHN: LAWYER_COLOR,
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
    BITCOIN_COLOR: r"bitcoin|block ?chain( capital)?|coins|cr[iy]pto(currency)?|e-currency|(jeffrey\s+)?wernick|(Howard\s+)?Lutnick|Libra|SpanCash|Tether|(zero\s+knowledge\s+|zk)pro(of|tocols?)",
    BUSINESS_COLOR: rf"(Steve\s+)?Wynn|(Leslie\s+)?Wexner|{NICHOLAS_RIBIS}|{ROBERT_LAWRENCE_KUHN}|{STEPHEN_HANSON}|{TERRY_KAFKA}",
    CHINA_COLOR: r"Beijing|CCP|Chin(a|ese)|Guo|Kwok|Tai(pei|wan)|Peking|PRC|xi",
    DEMOCRATS_COLOR: r"Biden|Maxine Waters|Obama|(Nancy )?Pelosi|Clinton|Hillary",
    ENTERTAINERS_COLOR: rf"Andres Serrano|Etienne Binant|Ramsey Elkholy|Woody( Allen)?",
    EUROPEAN_COLOR: r"Le\s*Pen|(Victor\s+)?Orbah?n",
    HARVARD_COLOR: rf"{LISA_NEW}|Harvard|MIT( Media Lab)?|Media Lab",
    INDIA_COLOR: rf"Ambani|Hardeep( puree)?|Indian?|Modi|mumbai|Zubair( Khan)?|{VINIT_SAHNI}",
    ISRAEL_COLOR: r"Bibi|(eh|Nili Priell )barak|Netanyahu|Israeli?",
    JOURNALIST_COLOR: rf"Alex Yablon|{PAUL_KRASSNER}|{MICHAEL_WOLFF}|Wolff|Susan Edelman",
    LAWYER_COLOR: rf"(Alan (M\. )?)?Dershowi(l|tz)|(Ken(neth W.)?\s+)?Starr|{DAVID_SCHOEN}|{JAY_LEFKOWITZ}|Lefkowitz|Lilly (Ann )?Sanchez|{MARTIN_WEINBERG}|{REID_WEINGARTEN}|Weinberg|Weingarten|Roy Black|{SCOTT_J_LINK}",
    MIDDLE_EAST_COLOR: rf"Abdulmalik Al-Makhlafi|Abu\s+Dhabi|{ANAS_ALRASHEED}|Assad|Dubai|Emir(ates)?|Erdogan|Gaddafi|HBJ|Imran Khan|Iran(ian)?|Islam(ic|ist)?|Istanbul|Kh?ashoggi|Kaz(akh|ich)stan|Kazakh?|KSA|MB(S|Z)|Mohammed\s+bin\s+Salman|Muslim|Pakistani?|Riya(dh|nd)|Saudi(\s+Arabian?)?|Shaher Abdulhak Besher|Sharia|Syria|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
    POLICE_COLOR: f"Police Code Enforcement|Ann Marie Villafana|Kirk Blouin",
    RUSSIA_COLOR: r"GRU|FSB|Lavrov|Moscow|(Vladimir )?Putin|Russian?|Vladimir Yudashkin",
    SCHOLAR_COLOR: rf"((Noam|Valeria) )?Chomsky|{DAVID_HAIG}|{JOSCHA_BACH}|Joscha|Bach|Moshe Hoffman|{ROBERT_TRIVERS}|Trivers",
    SOUTH_AMERICA_COLOR: r"Argentina|Bra[sz]il(ian)?|Bolsonar[aio]|Lula|(Nicolas )?Maduro|Venezuelan?s?",
    TRUMP_COLOR: r"(Donald\s+(J\.\s+)?)?Trump|Donald|DJT|Roger\s+Stone",
    COUNTERPARTY_COLORS[GHISLAINE_MAXWELL]: r"GMAX|gmax1@ellmax.com",
    COUNTERPARTY_COLORS[TERJE]: r"Terje (R[øo]e?d[- ])?Lars[eo]n",
    COUNTERPARTY_COLORS[JEFFREY_EPSTEIN]: EMAILER_REGEXES[JEFFREY_EPSTEIN].pattern + r'|Mark (L. )?Epstein',
    'orchid1': r"(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre|Virginia\s+Roberts",
    VC_COLOR: r"Masa(yoshi)?( Son)?|Najeev|Softbank",
    'turquoise4': r"BG|Bill\s+((and|or)\s+Melinda\s+)?Gates|Melinda(\s+Gates)?",
    BANK_COLOR: r"Black(rock|stone)|DB|Deutsche Bank|Goldman( ?Sachs)|Morgan Stanley|j\.?p\.? ?morgan( Chase)?|Chase Bank|us.gio@jpmorgan.com",
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

if args.suppress_output:
    print(f"Suppressing terminal output because args.suppress_output={args.suppress_output}...")
    CONSOLE_ARGS.update({'file': open(devnull, "wt")})

console = Console(**CONSOLE_ARGS)


# This is after the Theme() instantiation because 'bg' is reserved'
COUNTERPARTY_COLORS.update({
    'Ivanka': JAVANKA_COLOR,
    'Joichi Ito': COUNTERPARTY_COLORS[JOI_ITO],
    'Jared Kushner': JAVANKA_COLOR,
    'jeevacation@gmail.com': COUNTERPARTY_COLORS[JEFFREY_EPSTEIN],
    'Paul Manafort': COUNTERPARTY_COLORS[STEVE_BANNON],
    'Miro': COUNTERPARTY_COLORS[MIROSLAV],
    'Scaramucci': COUNTERPARTY_COLORS[SCARAMUCCI],
})


def make_link_markup(url: str, link_text: str, style: str | None = ARCHIVE_LINK_COLOR) -> str:
    return wrap_in_markup_style(f"[underline][link={url}]{link_text}[/link][/underline]", style)


def make_link(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(make_link_markup(url, link_text, f"{style} bold"))  # TODO: shouldn't add 'bold'


def archive_link(filename: str, style: str = ARCHIVE_LINK_COLOR, link_txt: str | None = None) -> Text:
    return make_link(search_archive_url(filename), link_txt or filename, style)


def coffeezilla_link(search_term: str, link_txt: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return make_link(search_archive_url(search_term), link_txt or search_term, style)


def get_style_for_name(name: str, default: str = DEFAULT) -> str:
    if name in COUNTERPARTY_COLORS:
        return COUNTERPARTY_COLORS[name]

    for style, name_regex in HIGHLIGHT_REGEXES.items():
        if name_regex.search(name):
            return style

    return default


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
        if last_name.lower() not in NAMES_TO_NOT_HIGHLIGHT:
            name_regex = re.compile(rf"(?!{first_name} ?)\b({last_name}s?)\b", re.IGNORECASE)
            text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

        # highlight first names
        if len(first_name) > 2 and first_name.lower() not in NAMES_TO_NOT_HIGHLIGHT:
            name_regex = re.compile(rf"\b({first_name}s?)\b(?! ?{last_name})", re.IGNORECASE)
            text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

    return text


def highlight_pattern(text: str, pattern: re.Pattern, style: str = 'cyan') -> Text:
    return Text.from_markup(pattern.sub(rf'[{style}]\1[/{style}]', text))


def print_centered(msg: str, style: str = '') -> None:
    console.print(Align.center(msg), style=style)


def print_centered_link(url: str, link_text: str, style: str | None = None) -> None:
    print_centered(make_link_markup(url, link_text, style))


def print_header():
    console.print(f"This site is not optimized for mobile but if you get past the header it should work ok.", style='dim')
    console.line()
    console.print(Panel(Text("Epstein Estate Documents - Seventh Production Collection Reformatted Text Messages", justify='center', style='bold reverse')))
    console.line()
    print_centered(make_link_markup(SUBSTACK_URL, "I Made Epstein's Text Messages Great Again (And You Should Read Them)", style=f'{HEADER_LINK} bold'))
    print_centered(make_link_markup(SUBSTACK_URL, SUBSTACK_URL.removeprefix('https://'), style='dodger_blue3'))
    print_centered(make_link_markup('https://cryptadamus.substack.com/', 'Substack', style=HEADER_LINK))
    print_centered(make_link_markup('https://universeodon.com/@cryptadamist/115572634993386057', 'Mastodon', style=HEADER_LINK))
    print_centered(make_link_markup('https://x.com/Cryptadamist/status/1990866804630036988', 'Twitter', style=HEADER_LINK))
    console.line()
    print_other_site_link()

    # Acronym table
    table = Table(title="Abbreviations Used Frequently In These Chats", show_header=True, header_style="bold")
    table.add_column("Abbreviation", justify="center", style='bold', width=19)
    table.add_column("Translation", style="white", justify="center")

    for k, v in HEADER_ABBREVIATIONS.items():
        table.add_row(highlight_text(k), v)

    console.print(Align.center(vertically_pad(table)))
    print_centered(make_link_markup(OVERSIGHT_REPUBLICANS_PRESSER_URL, 'Oversight Committee Releases Additional Epstein Estate Documents'))
    print_centered(make_link_markup(COFFEEZILLA_ARCHIVE_URL, 'Coffeezilla Archive Of Raw Epstein Materials'))
    print_centered(make_link_markup(JMAIL_URL, 'Jmail') + " (read His Emails via Gmail interface)")
    print_centered(make_link_markup(COURIER_NEWSROOM_ARCHIVE_URL, "Courier Newsroom's Searchable Archive"))
    print_centered(make_link_markup(f"{EPSTEINIFY_URL}/names", 'epsteinify.com') + " (raw document images)")
    print_centered(make_link_markup(RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL, 'Google Drive Raw Documents'))
    console.line()
    print_centered(make_link_markup(ATTRIBUTIONS_URL, "Explanation of Author Attributions", style='magenta'))
    print_centered(f"(thanks to {make_link_markup('https://x.com/ImDrinknWyn', '@ImDrinknWyn', 'dodger_blue3')} and others for attribution help)")
    print_centered(f"If you think there's an attribution error or can deanonymize an {UNKNOWN} contact {make_link_markup('https://x.com/cryptadamist', '@cryptadamist')}.", 'dim')
    print_centered('(note this site is based on the OCR text provided by Congress which is not the greatest)', 'dim')


def print_author_header(msg: str, color: str | None) -> None:
    txt = Text(msg, justify='center')
    color = 'white' if color == DEFAULT else (color or 'white')
    panel = Panel(txt, width=80, style=f"black on {color or 'white'} bold")
    console.print('\n', Align.center(panel), '\n')


def print_numbered_list(_list: list[str] | dict) -> None:
    for i, name in enumerate(_list):
        name = name or UNKNOWN
        console.print(Text(f"   {i}. ").append(name, style=get_style_for_name(name, DEFAULT_NAME_COLOR)))


def print_other_site_link() -> None:
    msg = 'The other site made by this code'
    url = ''

    if args.all:
        msg += " for Epstein's text messages"
        url = TEXT_MSGS_URL
    else:
        msg += ' has [italic]all[/italic] of His Emails'
        url = ALL_EMAILS_URL

    markup_msg = make_link_markup(url, msg, 'chartreuse3')
    print_centered(Text('(') + Text.from_markup(markup_msg).append(')'), style='bold')


def print_panel(msg: str, style: str = 'black on white', padding: tuple = (0, 0, 0, 0)) -> None:
    console.print(Padding(Panel(Text.from_markup(msg, justify='center'), width=70, style=style), padding))
    console.line()


def print_section_header(msg: str, style: str = SECTION_HEADER_STYLE, is_centered: bool = False) -> None:
    panel = Panel(Text(msg, justify='center'), expand=True, padding=(1, 1), style=style)

    if is_centered:
        panel = Align.center(panel)

    console.print(Padding(panel, (3, 0, 1, 0)))


def vertically_pad(obj: RenderResult) -> Padding:
    return Padding(obj, VERTICAL_PADDING)


def wrap_in_markup_style(msg: str, style: str | None = None) -> str:
    if style is None or len(style.strip()) == 0:
        return msg

    for style_word in style.split():
        msg = f"[{style_word}]{msg}[/{style_word}]"

    return msg


if deep_debug:
    console.print('KNOWN_IMESSAGE_FILE_IDS\n--------------')
    console.print(json.dumps(KNOWN_IMESSAGE_FILE_IDS))
    console.print('\n\n\nGUESSED_IMESSAGE_FILE_IDS\n--------------')
    console.print_json(json.dumps(GUESSED_IMESSAGE_FILE_IDS))
    console.line(2)
