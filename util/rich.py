# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
import json
import re
from os import devnull
from typing import Literal

from rich.align import Align
from rich.console import Console, RenderableType
from rich.highlighter import RegexHighlighter
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .constants import *
from .env import args, deep_debug, is_debug, logger
from .html import PAGE_TITLE

COLOR_SUFFIX = '_COLOR'

# Constant variables that end in "_COLOR" will be scanned to create the color highlight guide table.
# Colors for highlighting members of groups
ARCHIVE_LINK_COLOR = 'slate_blue3'
BANK_COLOR = 'green'
BITCOIN_COLOR = 'orange1 bold'
BUSINESS_COLOR = 'spring_green4'
BRO_COLOR = 'tan'
CHINA_COLOR = 'bright_red'
DEMOCRATS_COLOR = 'sky_blue1'
EMPLOYEE_COLOR = 'deep_sky_blue4'
ENTERTAINERS_COLOR = 'light_steel_blue3'
EUROPE_COLOR = 'light_sky_blue3'
HARVARD_COLOR = 'deep_pink2'
MODELING_COLOR = 'pale_violet_red1'
INDIA_COLOR = 'bright_green'
ISRAEL_COLOR = 'dodger_blue2'
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
# Personal colors
ARIANE_DE_ROTHSCHILD_COLOR = 'indian_red'
BANNON_COLOR = 'color(58)'
BILL_GATES_COLOR = 'turquoise4'
DEEPAK_CHOPRA_COLOR = 'dark_goldenrod'
DUBIN_COLOR = 'medium_orchid1'
GHISLAINE_MAXWELL_COLOR = 'deep_pink3'
JAVANKA_COLOR = 'medium_violet_red'  # TODO: make trump color?
JEFFREY_EPSTEIN_COLOR = 'blue1'
JABOR_Y_COLOR = "spring_green1"
JOI_ITO_COLOR = 'blue_violet'
KATHY_RUEMMLER_COLOR = 'magenta2'
LINDA_STONE_COLOR = 'pink3'
MELANIE_SPINELLA_COLOR = 'magenta3'
MELANIE_WALKER_COLOR = 'light_pink3'
PAULA_COLOR = 'pink1'
PRINCE_ANDREW_COLOR = 'dodger_blue1'
SOON_YI_COLOR = 'hot_pink'
SULTAN_BIN_SULAYEM_COLOR = 'green1'
# Other styles
DEFAULT_NAME_COLOR = 'gray46'
HEADER_FIELD_COLOR = 'plum4'
SENT_FROM_COLOR = 'gray42 italic'
SNIPPED_SIGNATURE_COLOR = 'gray19'
UNKNOWN_COLOR = 'cyan'

COLOR_MAPPING = {
    v: k.removesuffix(COLOR_SUFFIX).lower()
    for k, v in locals().items()
    if k.endswith(COLOR_SUFFIX)
}

# Theme style names
REGEX_STYLE_PREFIX = 'regex'
PHONE_NUMBER = 'phone_number'
TEXT_LINK = 'text_link'
TIMESTAMP = 'timestamp'

# Other styles
TITLE_STYLE = 'black on bright_white bold'
SECTION_HEADER_STYLE = 'bold white on blue3'
SOCIAL_MEDIA_LINK_STYLE = 'cadet_blue'

# Misc
LEADING_WHITESPACE_REGEX = re.compile(r'\A\s*', re.MULTILINE)
NON_ALPHA_CHARS_REGEX = re.compile(r'[^a-zA-Z0-9 ]')
MAX_PREVIEW_CHARS = 300
NUM_COLOR_KEY_COLS = 3
OUTPUT_WIDTH = 120

# Order matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_PRINTED_LIST = [
    JEREMY_RUBIN,
    JOI_ITO,
    AL_SECKEL,
    JABOR_Y,
    DANIEL_SIAD,
    JEAN_LUC_BRUNEL,
    EHUD_BARAK,
    MARTIN_NOWAK,
    'Masha Drokova',
    STEVE_BANNON,
    ARIANE_DE_ROTHSCHILD,
    OLIVIER_COLOM,
    BORIS_NIKOLIC,
    PRINCE_ANDREW,
    TOM_PRITZKER,
    'Jide Zeitlin',
    DAVID_STERN,
    MOHAMED_WAHEED_HASSAN,
    None,
]

# Order matters (will be order of output)
PEOPLE_WHOSE_EMAILS_SHOULD_BE_TABLES_LIST = [
    GHISLAINE_MAXWELL,
    LEON_BLACK,
    LANDON_THOMAS,
    KATHY_RUEMMLER,
    DARREN_INDYKE,
    RICHARD_KAHN,
    TYLER_SHEARS,
    SULTAN_BIN_SULAYEM,
    DEEPAK_CHOPRA,
]

highlighter_style_name = lambda style_name: f"{REGEX_STYLE_PREFIX}.{style_name.replace(' ', '_')}"

THEME_STYLES = {
    DEFAULT: 'wheat4',
    PHONE_NUMBER: 'bright_green',
    TEXT_LINK: 'deep_sky_blue4 underline',
    TIMESTAMP: 'gray30',
}

SCARAMUCCI_PATTERN = r"mooch|(Anthony ('The Mooch' )?)?Scaramucci"  # TODO: integrate

HIGHLIGHT_PATTERNS: dict[str, str] = {
    BANK_COLOR: fr"{ALIREZA_ITTIHADIEH}|Amanda\s*Ens|Black(rock|stone)|{DANIEL_SABBA}|DB|Deutsche Bank|Goldman( ?Sachs)|HSBC|(Janet\s*)?Yellen|(Jide\s*)?Zeitlin|(Jerome\s*)?Powell|Jes\s+Staley|Merrill\s+Lynch|Morgan Stanley|j\.?p\.?\s*morgan( Chase)?|Chase Bank|us.gio@jpmorgan.com|Marc\s*Leon|{LEON_BLACK}|{PAUL_MORRIS}|{PAUL_BARRETT}",
    BITCOIN_COLOR: fr"bitcoin|block ?chain( capital)?|Brock|coins|cr[iy]?pto(currency)?|e-currency|(Howard\s+)?Lutnick|(jeffrey\s+)?wernick|{JEREMY_RUBIN}|Libra|SpanCash|Tether|(zero\s+knowledge\s+|zk)pro(of|tocols?)",
    BRO_COLOR: fr"{JONATHAN_FARKAS}|{TOM_BARRACK}",
    BUSINESS_COLOR: fr"{emailer_pattern(BORIS_NIKOLIC)}|Marc Rich|(Steve\s+)?Wynn|(Leslie\s+)?Wexner|{BARBRO_EHNBOM}|{NICHOLAS_RIBIS}|{ROBERT_LAWRENCE_KUHN}|{STEPHEN_HANSON}|{TERRY_KAFKA}|{TOM_PRITZKER}",
    CHINA_COLOR: r"Beijing|CCP|Chin(a|ese)|Gino Yu|Guo|Kwok|Tai(pei|wan)|Peking|PRC|xi",
    DEEPAK_CHOPRA_COLOR: r"(Deepak )?Chopra|Deepak|Carolyn Rangel",
    DEMOCRATS_COLOR: r"Biden|(Bill )?Clinton|Hillary|Democrat(ic)?|(John )?Kerry|Maxine\s*Waters|(Barack )?Obama|(Nancy )?Pelosi|Ron\s*Dellums",
    DUBIN_COLOR: fr"((Celina|Eva( Anderss?on)?|Glenn) )?Dubin",
    EMPLOYEE_COLOR: fr"{LESLEY_GROFF}|{NADIA_MARCINKO}|{emailer_pattern(LAWRANCE_VISOSKI)}",
    ENTERTAINERS_COLOR: rf"Andres Serrano|Bill Siegel|Bobby slayton|David Blaine|Etienne Binant|Ramsey Elkholy|Steven Gaydos?|Woody( Allen)?",
    EUROPE_COLOR: fr"{MIROSLAV}|Miro(slav)?|(Caroline|Jack)?\s*Lang(, Caroline)?|Le\s*Pen|Macron|(Angela )?Merk(el|le)|(Sebastian )?Kurz|(Vi(c|k)tor\s+)?Orbah?n|((Lord|Peter) )?Mandelson|Terje(( (R[øo]e?d[- ])?)?Lars[eo]n)?|Edward Rod Larsen|Ukrain(e|ian)|Zug|{emailer_pattern(THORBJORN_JAGLAND)}",
    HARVARD_COLOR: fr"{LISA_NEW}|Harvard|MIT( Media Lab)?|Media Lab|{emailer_pattern(LARRY_SUMMERS)}|{emailer_pattern(MARTIN_NOWAK)}",
    INDIA_COLOR: fr"Ambani|{ANIL}|Hardeep( puree)?|Indian?|Modi|mumbai|Zubair( Khan)?|{VINIT_SAHNI}",
    ISRAEL_COLOR: r"Bibi|(eh|(Ehud|Nili Priell) )?barak|Mossad|Netanyahu|Israeli?",
    JAVANKA_COLOR: fr"Ivanka( Trump)?|(Jared )?Kushner|Jared",
    JOURNALIST_COLOR: rf"Alex Yablon|{emailer_pattern(EDWARD_EPSTEIN)}|{emailer_pattern(LANDON_THOMAS)}|{PAUL_KRASSNER}|{MICHAEL_WOLFF}|Wolff|Susan Edelman|[-\w.]+@(bbc|independent|mailonline|mirror|thetimes)\.co\.uk",
    LAWYER_COLOR: rf"{emailer_pattern(DARREN_INDYKE)}|{emailer_pattern(RICHARD_KAHN)}|{emailer_pattern(BRAD_KARP)}|(Alan (M\. )?)?Dershowi(l|tz)|{emailer_pattern(DAVID_STERN)}|(Erika )?Kellerhals|(Ken(neth W.)?\s+)?Starr|{DAVID_SCHOEN}|{JACK_GOLDBERGER}|{JAY_LEFKOWITZ}|Lefkowitz|Lilly (Ann )?Sanchez|{MARTIN_WEINBERG}|Michael J. Pike|Paul Weiss|{REID_WEINGARTEN}|Weinberg|Weingarten|Roy Black|{SCOTT_J_LINK}",
    LOBBYIST_COLOR: fr"{OLIVIER_COLOM}|Purevsuren Lundeg|Rob Crowe|Stanley Rosenberg", # lundeg mongolian ambassador, Rosenberg former state senator?
    MIDDLE_EAST_COLOR: rf"{emailer_pattern(MOHAMED_WAHEED_HASSAN)}|Abdulmalik Al-Makhlafi|Abu\s+Dhabi|{ANAS_ALRASHEED}|Assad|{AZIZA_ALAHMADI}|Dubai|Emir(ates)?|Erdogan|Gaddafi|HBJ|Imran Khan|Iran(ian)?|Islam(ic|ist)?|Istanbul|Kh?ashoggi|Kaz(akh|ich)stan|Kazakh?|KSA|MB(S|Z)|Mohammed\s+bin\s+Salman|Muslim|Pakistani?|Raafat\s*Alsabbagh|Riya(dh|nd)|Saudi(\s+Arabian?)?|Shaher( Abdulhak Besher)?|Sharia|Syria|Turk(ey|ish)|UAE|((Iraq|Iran|Kuwait|Qatar|Yemen)i?)",
    MODELING_COLOR: rf'{emailer_pattern(JEAN_LUC_BRUNEL)}|{DANIEL_SIAD}|Faith Kates?|\w+@mc2mm.com|{MARIANA_IDZKOWSKA}',
    POLICE_COLOR: rf"Ann Marie Villafana|(James )?Comey|Kirk Blouin|((Bob|Robert) )?Mueller|Police Code Enforcement",
    PUBLICIST_COLOR: rf"{AL_SECKEL}|{CHRISTINA_GALBRAITH}|Henry Holt|Ian Osborne|Matthew Hiltzik|{PEGGY_SIEGAL}|{TYLER_SHEARS}|ross@acuityreputation.com|Citrick|{emailer_pattern(MICHAEL_SITRICK)}",
    REPUBLICANS_COLOR: r"bolton|Broidy|(?!Merwin Dela )Cruz|kudlow|lewandowski|mattis|mnuchin|(Paul )?Manafort|Pompeo|Republican",
    RUSSIA_COLOR: fr"GRU|FSB|Lavrov|Masha\s*Drokova|Moscow|(Oleg )?Deripaska|(Vladimir )?Putin|Russian?|Rybolo(olev|vlev)|Vladimir Yudashkin",
    SCHOLAR_COLOR: fr"((Noam|Valeria) )?Chomsky|David Grosof|{DAVID_HAIG}|{JOSCHA_BACH}|Joscha|Bach|Moshe Hoffman|Peter Attia|{ROBERT_TRIVERS}|Trivers|{STEVEN_PFEIFFER}|{emailer_pattern(LAWRENCE_KRAUSS)}",
    SOUTH_AMERICA_COLOR: r"Argentina|Bra[sz]il(ian)?|Bolsonar[aio]|Lula|(Nicolas )?Maduro|Venezuelan?s?",
    TECH_BRO_COLOR: fr"Elon|Musk|Masa(yoshi)?( Son)?|Najeev|Reid Hoffman|(Peter )?Th(ie|ei)l|Softbank|{emailer_pattern(STEVEN_SINOFSKY)}",
    TRUMP_COLOR: r"DJT|(Donald\s+(J\.\s+)?)?Trump|Don(ald| Jr)(?! Rubin)|(Matt(hew)? )?Calamari|Roger\s+Stone",
    VICTIM_COLOR: r"(Virginia\s+((L\.?|Roberts)\s+)?)?Giuffre|Virginia\s+Roberts",
    VIRGIN_ISLANDS_COLOR: fr'Cecile de Jongh|(Kenneth E\. )?Mapp|{STACY_PLASKETT}',
    # Individuals' styles
    ARIANE_DE_ROTHSCHILD_COLOR: emailer_pattern(ARIANE_DE_ROTHSCHILD),
    BANNON_COLOR: r"((Steve|Sean)\s+)?Bannon",
    BILL_GATES_COLOR: r"BG|(Bill\s+((and|or)\s+Melinda\s+)?)?Gates|Melinda(\s+Gates)?",
    BITCOIN_COLOR.removesuffix(' bold'): SCARAMUCCI_PATTERN,
    GHISLAINE_MAXWELL_COLOR: r"Ghislaine|Maxwell|GMAX|gmax1@ellmax.com",
    JABOR_Y_COLOR: emailer_pattern(JABOR_Y),
    JEFFREY_EPSTEIN_COLOR: emailer_pattern(JEFFREY_EPSTEIN) + r'|Mark (L. )?Epstein',
    JOI_ITO_COLOR: emailer_pattern(JOI_ITO),
    KATHY_RUEMMLER_COLOR: emailer_pattern(KATHY_RUEMMLER),
    LINDA_STONE_COLOR: emailer_pattern(LINDA_STONE),
    MELANIE_SPINELLA_COLOR: emailer_pattern(MELANIE_SPINELLA),
    MELANIE_WALKER_COLOR: emailer_pattern(MELANIE_WALKER),
    PAULA_COLOR: emailer_pattern(PAULA),
    PRINCE_ANDREW_COLOR: emailer_pattern(PRINCE_ANDREW),
    SOON_YI_COLOR: emailer_pattern(SOON_YI),
    SULTAN_BIN_SULAYEM_COLOR: emailer_pattern(SULTAN_BIN_SULAYEM),
    # Misc
    HEADER_FIELD_COLOR: r"^(Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):",
    SENT_FROM_COLOR: SENT_FROM_REGEX.pattern,
    SNIPPED_SIGNATURE_COLOR: r'<\.\.\.(snipped|trimmed).*\.\.\.>',
    #UNKNOWN_COLOR: UNKNOWN.replace('(', '\\(').replace(')', '\\)'),
    UNKNOWN_COLOR: r"\(unknown\)",
}

# Wrap in \b, add optional s? at end of all regex patterns
HIGHLIGHT_REGEXES: dict[str, re.Pattern] = {
    # [\b\n] or no trailing \b is required for cases when last char in match is not a word char (e.g. when it's '.')
    k: re.compile(fr"\b(({v})s?)\b", re.I) if k not in [HEADER_FIELD_COLOR, UNKNOWN_COLOR] else re.compile(v, re.MULTILINE)
    for k, v in HIGHLIGHT_PATTERNS.items()
}

HIGHLIGHTER_REGEXES: list[re.Pattern] = []

for style, pattern in HIGHLIGHT_PATTERNS.items():
    if style not in COLOR_MAPPING:
        logger.warning(f"Skipping style '{style}' for highlighter...")
        continue

    style_name = COLOR_MAPPING[style]
    prefixed_style_name = highlighter_style_name(style_name)

    if prefixed_style_name in THEME_STYLES:
        raise RuntimeError(f"'{prefixed_style_name}' already in THEME_STYLE!")

    if style in [HEADER_FIELD_COLOR, SENT_FROM_COLOR, SNIPPED_SIGNATURE_COLOR, UNKNOWN_COLOR]:
        regex = re.compile(fr"(?P<{style_name}>{pattern})", re.IGNORECASE | re.MULTILINE)
        print(f"style regex for '{style}': {regex.pattern}")
    else:
        regex = re.compile(fr"\b(?P<{style_name}>({pattern})s?)\b", re.IGNORECASE)

    HIGHLIGHTER_REGEXES.append(regex)
    THEME_STYLES[prefixed_style_name] = style


class InterestingNamesHighlighter(RegexHighlighter):
    base_style = f"{REGEX_STYLE_PREFIX}."
    highlights = HIGHLIGHTER_REGEXES


highlighter = InterestingNamesHighlighter()

# Instantiate console object
CONSOLE_ARGS = {
    'color_system': '256',
    'highlighter': highlighter,
    'record': True,
    'theme': Theme(THEME_STYLES),
    'width': OUTPUT_WIDTH,
}

if args.suppress_output:
    logger.warning(f"Suppressing terminal output because args.suppress_output={args.suppress_output}...")
    CONSOLE_ARGS.update({'file': open(devnull, "wt")})

console = Console(**CONSOLE_ARGS)


def get_style_for_name(name: str, default: str = DEFAULT) -> str:
    for style, name_regex in HIGHLIGHT_REGEXES.items():
        if name_regex.search(name):
            return style

    return default


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


def print_author_header(msg: str, color: str | None) -> None:
    txt = Text(msg, justify='center')
    color = 'white' if color == DEFAULT else (color or 'white')
    panel = Panel(txt, width=80, style=f"black on {color or 'white'} bold")
    console.print('\n', Align.center(panel), '\n')


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
        table.add_row(highlighter(k), v)

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


def print_color_key(color_keys: Text, key_type: Literal["Groups", "People"]) -> None:
    color_table = Table(show_header=False, title=f'Rough Guide to Highlighted Colors for {key_type}')
    num_colors = len(color_keys)
    row_number = 0

    for i in range(0, NUM_COLOR_KEY_COLS):
        color_table.add_column(f"color_col_{i}", justify='center')

    while (row_number * NUM_COLOR_KEY_COLS) < num_colors:
        idx = row_number * NUM_COLOR_KEY_COLS

        color_table.add_row(
            color_keys[idx],
            color_keys[idx + 1] if (idx + 1) < num_colors else '',
            color_keys[idx + 2] if (idx + 2) < num_colors else '',
        )

        row_number += 1

    print_centered(vertically_pad(color_table))


def print_json(label: str, obj: object) -> None:
    console.print(f"{label}:\n")
    console.print_json(json.dumps(obj, indent=4, sort_keys=True))
    console.line(2)


def print_numbered_list_of_emailers(_list: list[str] | dict, esptein_files = None) -> None:
    """Add the first emailed_at for this emailer if 'epstein_files' provided."""
    console.line()

    for i, name in enumerate(_list):
        txt = Text(F"   {i + 1}. ")

        if esptein_files:
            earliest_email_date = (esptein_files.earliest_email_at(name) or FALLBACK_TIMESTAMP).date()
            txt.append(f"({earliest_email_date}) ", style='dim')

        console.print(txt.append(highlighter(name or UNKNOWN)))

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


if is_debug:
    console.line(2)
    print_json('HIGHLIGHTER_REGEXES', [r.pattern for r in HIGHLIGHTER_REGEXES])
    print_json('THEME_STYLES', THEME_STYLES)

if deep_debug:
    console.print('KNOWN_IMESSAGE_FILE_IDS\n--------------')
    console.print(json.dumps(KNOWN_IMESSAGE_FILE_IDS))
    console.print('\n\n\nGUESSED_IMESSAGE_FILE_IDS\n--------------')
    console.print_json(json.dumps(GUESSED_IMESSAGE_FILE_IDS))
    console.line(2)
