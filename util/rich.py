# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
import json
import re
from os import devnull

from rich.align import Align
from rich.console import Console, RenderableType
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .constants import *
from .data import flatten
from .env import args, deep_debug, logger
from .html import PAGE_TITLE
from .strings import regex_escape_periods
from .text_highlighter import EpsteinTextHighlighter

LEADING_WHITESPACE_REGEX = re.compile(r'\A\s*', re.MULTILINE)
NON_ALPHA_CHARS_REGEX = re.compile(r'[^a-zA-Z0-9 ]')
MAX_PREVIEW_CHARS = 300
NUM_COLOR_KEY_COLS = 3
OUTPUT_WIDTH = 120

# Constant variables that end in "_COLOR" will be scanned to create the color highlight guide table.
ARCHIVE_LINK_COLOR = 'slate_blue3'
BANK_COLOR = 'green'
BANNON_COLOR = 'color(58)'
BITCOIN_COLOR = 'orange1 bold'
BUSINESS_COLOR = 'spring_green4'
BRO_COLOR = 'tan'
CHINA_COLOR = 'bright_red'
DEFAULT_NAME_COLOR = 'gray46'
DEMOCRATS_COLOR = 'sky_blue1'
DUBIN_COLOR = 'medium_orchid1'
EMPLOYEE_COLOR = 'deep_sky_blue4'
ENTERTAINERS_COLOR = 'light_steel_blue3'
EUROPE_COLOR = 'light_sky_blue3'
HARVARD_COLOR = 'deep_pink2'
MODELING_COLOR = 'pale_violet_red1'
INDIA_COLOR = 'bright_green'
ISRAEL_COLOR = 'dodger_blue2'
JAVANKA_COLOR = 'medium_violet_red'
JOURNALIST_COLOR = 'bright_yellow'
LAWYER_COLOR = 'medium_purple2'
LOBBYIST_COLOR = 'light_coral'
MIDDLE_EAST_COLOR = 'dark_sea_green4'
POLICE_COLOR = 'color(24)'
PUBLICIST_COLOR = 'orange_red1'
RUSSIA_COLOR = 'red bold'
REPUBLICANS_COLOR = 'dark_red'
SCHOLAR_COLOR = 'light_goldenrod2'
SOUTH_AMERICA_COLOR = 'yellow'
TECH_BRO_COLOR = 'cyan2'  #dark_slate_gray3
TRUMP_COLOR = 'red3 bold'
VICTIM_COLOR = 'orchid1'
VIRGIN_ISLANDS_COLOR = 'sea_green1'

# Theme style names
ARCHIVE_LINK = 'archive_link'
COLOR_SUFFIX = '_COLOR'
HEADER_STYLE_NAME = 'header_field'
PHONE_NUMBER = 'phone_number'
SENT_FROM = 'sent_from'
TEXT_LINK = 'text_link'
TIMESTAMP = 'timestamp'

# Other styles
TITLE_STYLE = 'black on bright_white bold'
SECTION_HEADER_STYLE = 'bold white on blue3'
SOCIAL_MEDIA_LINK_STYLE = 'cadet_blue'

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

# Order matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED = {
    JEREMY_RUBIN: BITCOIN_COLOR,
    JOI_ITO: 'blue_violet',
    AL_SECKEL: 'orange_red1',
    JABOR_Y: "spring_green1",
    DANIEL_SIAD: MODELING_COLOR,
    JEAN_LUC_BRUNEL: MODELING_COLOR,
    EHUD_BARAK: ISRAEL_COLOR,
    MARTIN_NOWAK: HARVARD_COLOR,
    'Masha Drokova': RUSSIA_COLOR,
    STEVE_BANNON: BANNON_COLOR,
    ARIANE_DE_ROTHSCHILD: 'indian_red',
    OLIVIER_COLOM: LOBBYIST_COLOR,
    BORIS_NIKOLIC: BUSINESS_COLOR,
    PRINCE_ANDREW: 'dodger_blue1',
    TOM_PRITZKER: BUSINESS_COLOR,
    'Jide Zeitlin': BANK_COLOR,
    DAVID_STERN: LAWYER_COLOR,
    MOHAMED_WAHEED_HASSAN: MIDDLE_EAST_COLOR,
    None: 'grey74',
}

# ORder matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES = {
    GHISLAINE_MAXWELL: 'deep_pink3',
    LEON_BLACK: BUSINESS_COLOR,
    LANDON_THOMAS: JOURNALIST_COLOR,  # NYT journo
    SULTAN_BIN_SULAYEM: 'green1',
    DARREN_INDYKE: LAWYER_COLOR,
    RICHARD_KAHN: LAWYER_COLOR,
    DEEPAK_CHOPRA: 'dark_goldenrod',
    # Temporary
    KATHY_RUEMMLER: 'magenta2',
    TYLER_SHEARS: PUBLICIST_COLOR,
}

# Color different counterparties differently
COUNTERPARTY_COLORS = {
    ALIREZA_ITTIHADIEH: MIDDLE_EAST_COLOR,  # Iranian / British?
    ANIL: INDIA_COLOR,
    BRAD_KARP: LAWYER_COLOR,
    'Carolyn Rangel': PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES[DEEPAK_CHOPRA],  # Works for Deepak
    CELINA_DUBIN: DUBIN_COLOR,
    DEFAULT: 'wheat4',
    EVA: 'orchid',
    'Eva Dubin': DUBIN_COLOR,
    GLENN_DUBIN: DUBIN_COLOR,
    JEFFREY_EPSTEIN: 'blue1',
    JONATHAN_FARKAS: BRO_COLOR,
    LINDA_STONE: 'pink3',
    MELANIE_SPINELLA: 'magenta3',
    MELANIE_WALKER: 'light_pink3',
    MIROSLAV: EUROPE_COLOR,
    PAUL_MORRIS: BANK_COLOR,
    PAULA: 'pink1',
    SOON_YI: 'hot_pink',
    SEAN_BANNON: BANNON_COLOR,
    TOM_BARRACK: BRO_COLOR,
    UNKNOWN: 'cyan',
}

highlighter_style_name = lambda style_name: f"{EMAIL_HEADER_FIELD}.{style_name}"

OTHER_STYLES = {
    ARCHIVE_LINK: 'deep_sky_blue4',
    PHONE_NUMBER: 'bright_green',
    TEXT_LINK: 'deep_sky_blue4 underline',
    TIMESTAMP: 'gray30',
    HEADER_STYLE_NAME: 'plum4',
    highlighter_style_name('email'): 'bright_cyan',
    SENT_FROM: 'gray50 italic dim',
}

COUNTERPARTY_COLORS.update(PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED)
COUNTERPARTY_COLORS.update(PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES)
COUNTERPARTY_COLORS.update(OTHER_STYLES)

HIGHLIGHT_PATTERNS: dict[str, str] = {
    BANK_COLOR: fr"Amanda Ens|Black(rock|stone)|{DANIEL_SABBA}|DB|Deutsche Bank|Goldman( ?Sachs)|Jes Staley|Morgan Stanley|j\.?p\.? ?morgan( Chase)?|Chase Bank|us.gio@jpmorgan.com|Marc Leon|{PAUL_MORRIS}|{PAUL_BARRETT}",
    BITCOIN_COLOR: r"bitcoin|block ?chain( capital)?|Brock|coins|cr[iy]pto(currency)?|e-currency|(jeffrey\s+)?wernick|(Howard\s+)?Lutnick|Libra|SpanCash|Tether|(zero\s+knowledge\s+|zk)pro(of|tocols?)",
    BUSINESS_COLOR: rf"Marc Rich|(Steve\s+)?Wynn|(Leslie\s+)?Wexner|{BARBRO_EHNBOM}|{NICHOLAS_RIBIS}|{ROBERT_LAWRENCE_KUHN}|{STEPHEN_HANSON}|{TERRY_KAFKA}|{TOM_PRITZKER}",
    CHINA_COLOR: r"Beijing|CCP|Chin(a|ese)|Gino Yu|Guo|Kwok|Tai(pei|wan)|Peking|PRC|xi",
    DEMOCRATS_COLOR: r"Biden|(Bill )?Clinton|Hillary|Democrat(ic)?|(John )?Kerry|Maxine\s*Waters|(Barack )?Obama|(Nancy )?Pelosi|Ron\s*Dellums",
    EMPLOYEE_COLOR: fr"{EMAILER_REGEXES[LAWRANCE_VISOSKI].pattern}|{LESLEY_GROFF}|{NADIA_MARCINKO}",
    ENTERTAINERS_COLOR: rf"Andres Serrano|Bobby slayton|David Blaine|Etienne Binant|Ramsey Elkholy|Steven Gaydos?|Woody( Allen)?",
    EUROPE_COLOR: fr"(Caroline|Jack)?\s*Lang(, Caroline)?|Le\s*Pen|Macron|(Angela )?Merk(el|le)|(Sebastian )?Kurz|(Vi(c|k)tor\s+)?Orbah?n|(Peter )?Mandelson|Terje(( (R[øo]e?d[- ])?)?Lars[eo]n)?|Edward Rod Larsen|Ukrain(e|ian)|Zug|{EMAILER_REGEXES[THORBJORN_JAGLAND].pattern}",
    HARVARD_COLOR: fr"{LISA_NEW}|Harvard|MIT( Media Lab)?|Media Lab|{EMAILER_REGEXES[LARRY_SUMMERS].pattern}",
    INDIA_COLOR: rf"Ambani|Hardeep( puree)?|Indian?|Modi|mumbai|Zubair( Khan)?|{VINIT_SAHNI}",
    ISRAEL_COLOR: r"Bibi|(eh|(Ehud|Nili Priell) )?barak|Mossad|Netanyahu|Israeli?",
    JOURNALIST_COLOR: rf"Alex Yablon|{EMAILER_REGEXES[EDWARD_EPSTEIN].pattern}|{PAUL_KRASSNER}|{MICHAEL_WOLFF}|Wolff|Susan Edelman|[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk",
    LAWYER_COLOR: rf"(Alan (M\. )?)?Dershowi(l|tz)|(Erika )?Kellerhals|(Ken(neth W.)?\s+)?Starr|{DAVID_SCHOEN}|{JAY_LEFKOWITZ}|Lefkowitz|Lilly (Ann )?Sanchez|{MARTIN_WEINBERG}|Paul Weiss|{REID_WEINGARTEN}|Weinberg|Weingarten|Roy Black|{SCOTT_J_LINK}",
    LOBBYIST_COLOR: r"Purevsuren Lundeg|Rob Crowe|Stanley Rosenberg", # lundeg mongolian ambassador, Rosenberg former state senator?
    MIDDLE_EAST_COLOR: rf"Abdulmalik Al-Makhlafi|Abu\s+Dhabi|{ANAS_ALRASHEED}|Assad|{AZIZA_ALAHMADI}|Dubai|Emir(ates)?|Erdogan|Gaddafi|HBJ|Imran Khan|Iran(ian)?|Islam(ic|ist)?|Istanbul|Kh?ashoggi|Kaz(akh|ich)stan|Kazakh?|KSA|MB(S|Z)|Mohammed\s+bin\s+Salman|Muslim|Pakistani?|Riya(dh|nd)|Saudi(\s+Arabian?)?|Shaher Abdulhak Besher|Sharia|Syria|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
    MODELING_COLOR: rf'{EMAILER_REGEXES[JEAN_LUC_BRUNEL].pattern}|{DANIEL_SIAD}|Faith Kates?|\w+@mc2mm.com|{MARIANA_IDZKOWSKA}',
    POLICE_COLOR: rf"Ann Marie Villafana|(James )?Comey|Kirk Blouin|((Bob|Robert) )?Mueller|Police Code Enforcement",
    PUBLICIST_COLOR: rf"{CHRISTINA_GALBRAITH}|Henry Holt|Ian Osborne|Matthew Hiltzik|{PEGGY_SIEGAL}|{TYLER_SHEARS}|ross@acuityreputation.com",
    REPUBLICANS_COLOR: r"bolton|Broidy|cruz|kudlow|lewandowski|mnuchin|Pompeo|Republican",
    RUSSIA_COLOR: fr"GRU|FSB|Lavrov|Moscow|(Oleg )?Deripaska|(Vladimir )?Putin|Russian?|Vladimir Yudashkin",
    SCHOLAR_COLOR: fr"((Noam|Valeria) )?Chomsky|David Grosof|{DAVID_HAIG}|{JOSCHA_BACH}|Joscha|Bach|Moshe Hoffman|Peter Attia|{ROBERT_TRIVERS}|Trivers|{STEVEN_PFEIFFER}|{EMAILER_REGEXES[LAWRENCE_KRAUSS].pattern}",
    SOUTH_AMERICA_COLOR: r"Argentina|Bra[sz]il(ian)?|Bolsonar[aio]|Lula|(Nicolas )?Maduro|Venezuelan?s?",
    TECH_BRO_COLOR: fr"Elon|Musk|Masa(yoshi)?( Son)?|Najeev|Reid Hoffman|(Peter )?Thiel|Softbank|{EMAILER_REGEXES[STEVEN_SINOFSKY].pattern}",
    TRUMP_COLOR: r"DJT|(Donald\s+(J\.\s+)?)?Trump|Don(ald| Jr)(?! Rubin)|Roger\s+Stone",
    VICTIM_COLOR: r"(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre|Virginia\s+Roberts",
    VIRGIN_ISLANDS_COLOR: fr'Cecile de Jongh|(Kenneth E\. )?Mapp|{STACY_PLASKETT}',
    # Individuals' colors
    BITCOIN_COLOR.removesuffix(' bold'): r"mooch|(Anthony ('The Mooch' )?)?Scaramucci",
    COUNTERPARTY_COLORS[GHISLAINE_MAXWELL]: r"GMAX|gmax1@ellmax.com",
    COUNTERPARTY_COLORS[JEFFREY_EPSTEIN]: EMAILER_REGEXES[JEFFREY_EPSTEIN].pattern + r'|Mark (L. )?Epstein',
    'turquoise4': r"BG|(Bill\s+((and|or)\s+Melinda\s+)?)?Gates|Melinda(\s+Gates)?",
    # Misc
    HEADER_STYLE_NAME: r"^((Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):)"
}

# Wrap in \b, add optional s? at end of all regex patterns
HIGHLIGHT_REGEXES: dict[str, re.Pattern] = {
    # [\b\n] or no trailing \b is required for cases when last char in match is not a word char (e.g. when it's '.')
    k: re.compile(fr"\b(({v})s?)\b", re.I) if k != HEADER_STYLE_NAME else re.compile(v, re.MULTILINE)
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

# This is after the Theme() instantiation because 'bg' is reserved'
COUNTERPARTY_COLORS.update({
    'Ivanka': JAVANKA_COLOR,
    'Joichi Ito': COUNTERPARTY_COLORS[JOI_ITO],
    'Jared Kushner': JAVANKA_COLOR,
    'Miro': COUNTERPARTY_COLORS[MIROSLAV],
    'Paul Manafort': REPUBLICANS_COLOR,
})


if args.no_highlights:
    COUNTERPARTY_COLORS = {}
    HIGHLIGHT_REGEXES = {}

if args.suppress_output:
    logger.warning(f"Suppressing terminal output because args.suppress_output={args.suppress_output}...")
    CONSOLE_ARGS.update({'file': open(devnull, "wt")})

console = Console(**CONSOLE_ARGS)


def get_style_for_name(name: str, default: str = DEFAULT) -> str:
    if name in COUNTERPARTY_COLORS:
        return COUNTERPARTY_COLORS[name]

    for style, name_regex in HIGHLIGHT_REGEXES.items():
        if name_regex.search(name):
            return style

    return default


def highlight_interesting_text(text: str) -> str:
    for style, name_regex in HIGHLIGHT_REGEXES.items():
        text = name_regex.sub(rf'[{style}]\1[/{style}]', text)

    for name, style in COUNTERPARTY_COLORS.items():
        if name in [None, DEFAULT, HEADER_STYLE_NAME, SENT_FROM]:
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


def highlight_regex_match(text: str, pattern: re.Pattern, style: str = 'cyan') -> Text:
    """Replace 'pattern' matches with markup of the match colored with 'style'."""
    return Text.from_markup(pattern.sub(rf'[{style}]\1[/{style}]', text))


def make_link_markup(url: str, link_text: str, style: str | None = ARCHIVE_LINK_COLOR, underline: bool = True) -> str:
    style = (style or '') + (' underline' if underline else '')
    return wrap_in_markup_style(f"[link={url}]{link_text}[/link]", style)


def make_link(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(make_link_markup(url, link_text, style))


def search_coffeezilla_link(text: str, link_txt: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return make_link(search_coffeezilla_url(text), link_txt or text, style)


def print_centered(obj: RenderableType, style: str = '') -> None:
    console.print(Align.center(obj), style=style)


def print_centered_link(url: str, link_text: str, style: str | None = None) -> None:
    print_centered(make_link_markup(url, link_text, style or ARCHIVE_LINK_COLOR))


def print_header():
    console.print(f"This site is not optimized for mobile but if you get past the header it should work ok.", style='dim')
    console.line()
    console.print(Panel(Text(PAGE_TITLE, justify='center'), style=TITLE_STYLE))
    console.line()
    print_centered_link(SUBSTACK_URL, "I Made Epstein's Text Messages Great Again (And You Should Read Them)", style=f'chartreuse1 bold')
    print_centered_link(SUBSTACK_URL, SUBSTACK_URL.removeprefix('https://'), style='dark_sea_green4 dim')
    print_centered_link('https://cryptadamus.substack.com/', 'Substack', style=SOCIAL_MEDIA_LINK_STYLE)
    print_centered_link('https://universeodon.com/@cryptadamist/115572634993386057', 'Mastodon', style=SOCIAL_MEDIA_LINK_STYLE)
    print_centered_link('https://x.com/Cryptadamist/status/1990866804630036988', 'Twitter', style=SOCIAL_MEDIA_LINK_STYLE)
    console.line()
    print_other_site_link()

    # Acronym table
    table = Table(title="Abbreviations Used Frequently In These Chats", show_header=True, header_style="bold")
    table.add_column("Abbreviation", justify="center", style='bold', width=19)
    table.add_column("Translation", style="white", justify="center")

    for k, v in HEADER_ABBREVIATIONS.items():
        table.add_row(highlight_interesting_text(k), v)

    console.print(Align.center(vertically_pad(table)))
    print_centered_link(OVERSIGHT_REPUBLICANS_PRESSER_URL, 'Oversight Committee Releases Additional Epstein Estate Documents')
    print_centered_link(COFFEEZILLA_ARCHIVE_URL, 'Coffeezilla Archive Of Raw Epstein Materials')
    print_centered(make_link_markup(JMAIL_URL, 'Jmail') + " (read His Emails via Gmail interface)")
    print_centered_link(COURIER_NEWSROOM_ARCHIVE_URL, "Courier Newsroom's Searchable Archive")
    print_centered(make_link_markup(f"{EPSTEINIFY_URL}/names", 'epsteinify.com') + " (raw document images)")
    print_centered_link(RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL, 'Google Drive Raw Documents')
    console.line()
    print_centered_link(ATTRIBUTIONS_URL, "some explanations of author attributions", style='magenta')
    print_centered(f"(thanks to {make_link_markup('https://x.com/ImDrinknWyn', '@ImDrinknWyn', 'dodger_blue3')} and others for attribution help)")
    print_centered(f"If you think there's an attribution error or can deanonymize an {UNKNOWN} contact {make_link_markup('https://x.com/cryptadamist', '@cryptadamist')}.", 'grey46')
    print_centered('(note this site is based on the OCR text provided by Congress which is not the greatest)', 'grey23')


def print_author_header(msg: str, color: str | None) -> None:
    txt = Text(msg, justify='center')
    color = 'white' if color == DEFAULT else (color or 'white')
    panel = Panel(txt, width=80, style=f"black on {color or 'white'} bold")
    console.print('\n', Align.center(panel), '\n')


def print_color_key(color_keys: Text) -> None:
    color_table = Table(show_header=False, title='Rough Guide to Highlighted Colors')
    num_colors = len(color_keys)
    row_number = 0

    for i in range(0, NUM_COLOR_KEY_COLS):
        color_table.add_column(f"color_col_{i}", justify='center', width=20)

    while (row_number * NUM_COLOR_KEY_COLS) < num_colors:
        idx = row_number * NUM_COLOR_KEY_COLS

        color_table.add_row(
            color_keys[idx],
            color_keys[idx + 1] if (idx + 1) < num_colors else '',
            color_keys[idx + 2] if (idx + 2) < num_colors else '',
        )

        row_number += 1

    print_centered(vertically_pad(color_table))


def print_numbered_list_of_emailers(_list: list[str] | dict, esptein_files = None) -> None:
    """Add the first emailed_at for this emailer if 'epstein_files' provided."""
    console.line()

    for i, name in enumerate(_list):
        txt = Text(F"   {i + 1}. ")

        if esptein_files:
            earliest_email_date = (esptein_files.earliest_email_at(name) or FALLBACK_TIMESTAMP).date()
            txt.append(f"({earliest_email_date}) ", style='dim')

        name = name or UNKNOWN
        console.print(txt + Text.from_markup(highlight_interesting_text(name)))

    console.line()


def print_other_site_link(is_header: bool = True) -> None:
    site_type = EMAIL if args.all else TEXT_MESSAGE

    if is_header:
        site_type = wrap_in_markup_style(f"  ******* This is the Epstein {site_type.title()}s site *******  ", TITLE_STYLE)
        print_centered(site_type)

    other_site_type = TEXT_MESSAGE if site_type == EMAIL else EMAIL
    other_site_msg = "there's a separate site for" + (' all of' if other_site_type == EMAIL else '')
    other_site_msg += f" Epstein's {other_site_type}s also generated by this code"
    markup_msg = make_link_markup(SITE_URLS[other_site_type], other_site_msg, 'dark_goldenrod')
    print_centered(Text('(') + Text.from_markup(markup_msg).append(')'), style='bold')


def print_panel(msg: str, style: str = 'black on white', padding: tuple | None = None) -> None:
    _padding = list(padding or [0, 0, 0, 0])
    _padding[2] += 1  # Bottom pad
    console.print(Padding(Panel(Text.from_markup(msg, justify='center'), width=70, style=style), tuple(_padding)))


def print_section_header(msg: str, style: str = SECTION_HEADER_STYLE, is_centered: bool = False) -> None:
    panel = Panel(Text(msg, justify='center'), expand=True, padding=(1, 1), style=style)
    panel = Align.center(panel) if is_centered else panel
    console.print(Padding(panel, (3, 0, 1, 0)))


def vertically_pad(obj: RenderableType, amount: int = 1) -> Padding:
    return Padding(obj,  (amount, 0, amount, 0))


def wrap_in_markup_style(msg: str, style: str | None = None) -> str:
    if style is None or len(style.strip()) == 0:
        return msg

    modifier = ''

    for style_word in style.split():
        if style_word == 'on':
            modifier = style_word
            continue

        style = f"{modifier} {style_word}".strip()
        msg = f"[{style}]{msg}[/{style}]"
        modifier = ''

    return msg


if deep_debug:
    console.print('KNOWN_IMESSAGE_FILE_IDS\n--------------')
    console.print(json.dumps(KNOWN_IMESSAGE_FILE_IDS))
    console.print('\n\n\nGUESSED_IMESSAGE_FILE_IDS\n--------------')
    console.print_json(json.dumps(GUESSED_IMESSAGE_FILE_IDS))
    console.line(2)
