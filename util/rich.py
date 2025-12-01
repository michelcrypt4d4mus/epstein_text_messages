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
from .file_helper import build_filename_for_id
from .highlighted_group import COLOR_KEYS, HIGHLIGHTED_GROUPS, REGEX_STYLE_PREFIX, HighlightedGroup
from .html import PAGE_TITLE

NUM_COLOR_KEY_COLS = 3
OUTPUT_WIDTH = 120

# Styles
ARCHIVE_LINK_COLOR = 'slate_blue3'
DEFAULT_NAME_COLOR = 'gray46'
SECTION_HEADER_STYLE = 'bold white on blue3'
SOCIAL_MEDIA_LINK_STYLE = 'cadet_blue'
TITLE_STYLE = 'black on bright_white bold'

# Theme style names
PHONE_NUMBER = 'phone_number'
TEXT_LINK = 'text_link'
TIMESTAMP = 'timestamp'

THEME_STYLES = {
    DEFAULT: 'wheat4',
    PHONE_NUMBER: 'bright_green',
    TEXT_LINK: 'deep_sky_blue4 underline',
    TIMESTAMP: 'gray30',
}

for highlight_group in HIGHLIGHTED_GROUPS:
    THEME_STYLES[highlight_group.style_name] = highlight_group.style


class InterestingNamesHighlighter(RegexHighlighter):
    base_style = f"{REGEX_STYLE_PREFIX}."
    highlights = [highlight_group.regex for highlight_group in HIGHLIGHTED_GROUPS]


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


def get_category_for_name(name: str) -> str | None:
    highlight_group = get_highlight_group_for_name(name)
    return highlight_group.label if highlight_group else None


def get_highlight_group_for_name(name: str) -> HighlightedGroup | None:
    for highlight_group in HIGHLIGHTED_GROUPS:
        if highlight_group.regex.search(name):
            return highlight_group


def get_style_for_name(name: str, default: str = DEFAULT) -> str:
    highlight_group = get_highlight_group_for_name(name)
    return highlight_group.style if highlight_group else default


def highlight_regex_match(text: str, pattern: re.Pattern, style: str = 'cyan') -> Text:
    """Replace 'pattern' matches with markup of the match colored with 'style'."""
    return Text.from_markup(pattern.sub(rf'[{style}]\1[/{style}]', text))


def make_epsteinify_doc_link_markup(filename_or_id: int | str, style: str = TEXT_LINK) -> str:
    if isinstance(filename_or_id, int) or not filename_or_id.startswith(HOUSE_OVERSIGHT_PREFIX):
        file_stem = build_filename_for_id(filename_or_id)
    else:
        file_stem = str(filename_or_id)

    return make_link_markup(epsteinify_doc_url(file_stem), file_stem, style)


def make_epsteinify_doc_link_txt(filename_or_id: int | str, style: str = TEXT_LINK) -> Text:
    return Text.from_markup(make_epsteinify_doc_link_markup(filename_or_id, style))


def make_link_markup(url: str, link_text: str, style: str | None = ARCHIVE_LINK_COLOR, underline: bool = True) -> str:
    style = (style or '') + (' underline' if underline else '')
    return wrap_in_markup_style(f"[link={url}]{link_text}[/link]", style)


def make_link(url: str, link_text: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return Text.from_markup(make_link_markup(url, link_text, style))


def search_coffeezilla_link(text: str, link_txt: str, style: str = ARCHIVE_LINK_COLOR) -> Text:
    return make_link(search_coffeezilla_url(text), link_txt or text, style)


def print_author_header(msg: str, color: str | None, footer: str | None = None) -> None:
    txt = Text(msg, justify='center')
    color = color or 'white'
    color = 'white' if color == DEFAULT else color
    panel = Panel(txt, width=80, style=f"black on {color} bold")
    console.print('\n', Align.center(panel))

    if footer:
        console.print(Align.center(f"({footer})"), style='dim italic')

    console.line()


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


def print_color_key(key_type: Literal["Groups", "People"] = "Groups") -> None:
    color_table = Table(show_header=False, title=f'Rough Guide to Highlighted Colors')
    num_colors = len(COLOR_KEYS)
    row_number = 0

    for i in range(0, NUM_COLOR_KEY_COLS):
        color_table.add_column(f"color_col_{i}", justify='center')

    while (row_number * NUM_COLOR_KEY_COLS) < num_colors:
        idx = row_number * NUM_COLOR_KEY_COLS

        color_table.add_row(
            COLOR_KEYS[idx],
            COLOR_KEYS[idx + 1] if (idx + 1) < num_colors else '',
            COLOR_KEYS[idx + 2] if (idx + 2) < num_colors else '',
        )

        row_number += 1

    print_centered(vertically_pad(color_table))


def print_json(label: str, obj: object) -> None:
    console.print(f"{label}:\n")
    console.print_json(json.dumps(obj, indent=4, sort_keys=True))
    console.line(2)


def print_numbered_list_of_emailers(_list: list[str] | dict, epstein_files = None) -> None:
    """Add the first emailed_at for this emailer if 'epstein_files' provided."""
    console.line()

    for i, name in enumerate(_list):
        txt = Text(F"   {i + 1}. ", style=DEFAULT_NAME_COLOR)

        if epstein_files:
            earliest_email_date = (epstein_files.earliest_email_at(name) or FALLBACK_TIMESTAMP).date()
            txt.append(escape(f"[{earliest_email_date}] "), style='dim')

        txt.append(highlighter(name or UNKNOWN))

        if epstein_files:
            txt.append(f" ({len(epstein_files.emails_for(name))} emails)", style='grey23 italic')

        console.print(txt)

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
    # print_json('HIGHLIGHTER_REGEXES', [r.pattern for r in HIGHLIGHTER_REGEXES])
    print_json('THEME_STYLES', THEME_STYLES)

if deep_debug:
    console.print('KNOWN_IMESSAGE_FILE_IDS\n--------------')
    console.print(json.dumps(KNOWN_IMESSAGE_FILE_IDS))
    console.print('\n\n\nGUESSED_IMESSAGE_FILE_IDS\n--------------')
    console.print_json(json.dumps(GUESSED_IMESSAGE_FILE_IDS))
    console.line(2)
