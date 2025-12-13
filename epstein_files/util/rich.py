# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
import json
from os import devnull
from pathlib import Path
from typing import Literal

from rich.align import Align
from rich.console import Console, RenderableType
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from epstein_files.util.constant.html import CONSOLE_HTML_FORMAT, HTML_TERMINAL_THEME, PAGE_TITLE
from epstein_files.util.constant.names import UNKNOWN
from epstein_files.util.constant.strings import DEFAULT, EMAIL, SiteType
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import FALLBACK_TIMESTAMP, HEADER_ABBREVIATIONS
from epstein_files.util.env import args, logger
from epstein_files.util.file_helper import file_size_str
from epstein_files.util.highlighted_group import COLOR_KEYS, HIGHLIGHTED_GROUPS, InterestingNamesHighlighter

DEFAULT_NAME_COLOR = 'gray46'
SECTION_HEADER_STYLE = 'bold white on blue3'
SOCIAL_MEDIA_LINK_STYLE = 'cadet_blue'
TITLE_STYLE = 'black on bright_white bold'
NUM_COLOR_KEY_COLS = 4

THEME_STYLES = {
    DEFAULT: 'wheat4',
    TEXT_LINK: 'deep_sky_blue4 underline',
}

for highlight_group in HIGHLIGHTED_GROUPS:
    THEME_STYLES[highlight_group.style_name] = highlight_group.style

highlighter = InterestingNamesHighlighter()

# Instantiate console object
CONSOLE_ARGS = {
    'color_system': '256',
    'highlighter': highlighter,
    'record': args.build,
    'safe_box': False,
    'theme': Theme(THEME_STYLES),
    'width': args.width,
}

if args.suppress_output:
    logger.warning(f"Suppressing terminal output because args.suppress_output={args.suppress_output}...")
    CONSOLE_ARGS.update({'file': open(devnull, "wt")})

console = Console(**CONSOLE_ARGS)


def parenthesize(msg: str | Text, style: str = '') -> Text:
    txt = Text(msg) if isinstance(msg, str) else msg
    return Text('(', style=style).append(txt).append(')')


def print_abbreviations_table() -> None:
    table = Table(title="Abbreviations Used Frequently In These Chats", header_style="bold")
    table.add_column("Abbreviation", justify="center", style='bold', width=19)
    table.add_column("Translation", style="white", justify="center")

    for k, v in HEADER_ABBREVIATIONS.items():
        table.add_row(highlighter(k), v)

    console.print(Align.center(vertically_pad(table)))


def print_author_header(msg: str, color: str | None, footer: str | None = None) -> None:
    txt = Text(msg, justify='center')
    color = color or 'white'
    color = 'white' if color == DEFAULT else color
    panel = Panel(txt, width=80, style=f"black on {color} bold")
    console.print('\n', Align.center(panel))

    if footer:
        console.print(Align.center(f"({footer})"), highlight=False, style=f'{color} italic')

    console.line()


def print_centered(obj: RenderableType, style: str = '') -> None:
    console.print(Align.center(obj), style=style)


def print_centered_link(url: str, link_text: str, style: str | None = None) -> None:
    print_centered(link_markup(url, link_text, style or ARCHIVE_LINK_COLOR))


def print_color_key(key_type: Literal["Groups", "People"] = "Groups") -> None:
    color_table = Table(title=f'Rough Guide to Highlighted Colors', show_header=False)
    num_colors = len(COLOR_KEYS)
    row_number = 0

    for i in range(0, NUM_COLOR_KEY_COLS):
        color_table.add_column(f"color_col_{i}", justify='center')

    while (row_number * NUM_COLOR_KEY_COLS) < num_colors:
        idx = row_number * NUM_COLOR_KEY_COLS
        color_table.add_row(*COLOR_KEYS[idx:(idx + NUM_COLOR_KEY_COLS)])
        row_number += 1

    print_centered(vertically_pad(color_table))


def print_header() -> None:
    console.print(f"This site is not optimized for mobile but if you get past the header it should work ok.", style='dim')
    print_page_title()
    print_other_site_link()
    print_abbreviations_table()
    print_centered_link(OVERSIGHT_REPUBLICANS_PRESSER_URL, 'Oversight Committee Releases Additional Epstein Estate Documents')
    print_centered_link(COFFEEZILLA_ARCHIVE_URL, 'Coffeezilla Archive Of Raw Epstein Materials')
    print_centered(link_markup(JMAIL_URL, JMAIL) + " (read His Emails via Gmail interface)")
    print_centered_link(COURIER_NEWSROOM_ARCHIVE_URL, "Courier Newsroom's Searchable Archive")
    print_centered(link_markup(f"{EPSTEINIFY_URL}/names", 'epsteinify.com') + " (raw document images)")
    print_centered_link(RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL, 'Google Drive Raw Documents')
    console.line()
    print_centered_link(ATTRIBUTIONS_URL, "some explanations of author attributions", style='magenta')
    print_centered(f"(thanks to {link_markup('https://x.com/ImDrinknWyn', '@ImDrinknWyn', 'dodger_blue3')} and others for attribution help)")
    print_centered(f"If you think there's an attribution error or can deanonymize an {UNKNOWN} contact {link_markup('https://x.com/cryptadamist', '@cryptadamist')}.", 'grey46')
    print_centered('(note this site is based on the OCR text provided by Congress which is not the greatest)', 'grey23')


def print_json(label: str, obj: object, skip_falsey: bool = False) -> None:
    if isinstance(obj, dict) and skip_falsey:
        obj = {k: v for k, v in obj.items() if v}

    console.line()
    console.print(Panel(label, expand=False))
    console.print_json(json.dumps(obj, sort_keys=True), indent=4)
    console.line()


def print_numbered_list_of_emailers(_list: list[str | None], epstein_files = None) -> None:
    """Add the first emailed_at timestamp for this emailer if 'epstein_files' provided."""
    console.line()

    for i, name in enumerate(_list):
        txt = Text((' ' if i < 9 else '') + F"   {i + 1}. ", style=DEFAULT_NAME_COLOR)

        if epstein_files:
            earliest_email_date = (epstein_files.earliest_email_at(name) or FALLBACK_TIMESTAMP).date()
            txt.append(escape(f"[{earliest_email_date}] "), style='grey23')

        txt.append(highlighter(name or UNKNOWN))

        if epstein_files:
            num_days_in_converation = epstein_files.email_conversation_length_in_days(name)
            msg = f" ({len(epstein_files.emails_for(name))} emails over {num_days_in_converation:,} days)"
            txt.append(msg, style=f'dim italic')

        console.print(txt)

    console.line()


def print_other_site_link(is_header: bool = True) -> None:
    """Print a link to the emails site if we're building text messages site and vice versa."""
    site_type = EMAIL if args.all_emails else TEXT_MESSAGE

    if is_header:
        print_starred_header(f"This is the Epstein {site_type.title()}s site")
        console.line()

    other_site_type: SiteType = TEXT_MESSAGE if site_type == EMAIL else EMAIL
    other_site_msg = "there's a separate site for" + (' all of' if other_site_type == EMAIL else '')
    other_site_msg += f" Epstein's {other_site_type}s also generated by this code"
    markup_msg = link_markup(SITE_URLS[other_site_type], other_site_msg, 'dark_goldenrod')
    print_centered(parenthesize(Text.from_markup(markup_msg)), style='bold')
    word_count_link = link_text_obj(WORD_COUNT_URL, 'most frequently used words in these emails', 'dark_goldenrod dim')
    print_centered(parenthesize(word_count_link))


def print_page_title(expand: bool = True) -> None:
    console.line()
    console.print(Align.center(Panel(Text(PAGE_TITLE, justify='center'), expand=expand, style=TITLE_STYLE)))
    console.line()
    print_social_media_links()
    console.line()


def print_panel(msg: str, style: str = 'black on white', padding: tuple | None = None, centered: bool = False) -> None:
    _padding = list(padding or [0, 0, 0, 0])
    _padding[2] += 1  # Bottom pad
    panel = Panel(Text.from_markup(msg, justify='center'), width=70, style=style)

    if centered:
        console.print(Align.center(Padding(panel, tuple(_padding))))
    else:
        console.print(Padding(panel, tuple(_padding)))


def print_section_header(msg: str, style: str = SECTION_HEADER_STYLE, is_centered: bool = False) -> None:
    panel = Panel(Text(msg, justify='center'), expand=True, padding=(1, 1), style=style)
    panel = Align.center(panel) if is_centered else panel
    console.print(Padding(panel, (3, 0, 1, 0)))


def print_social_media_links() -> None:
    print_centered_link(SUBSTACK_URL, "I Made Epstein's Text Messages Great Again (And You Should Read Them)", style=f'chartreuse1 bold')
    print_centered_link(SUBSTACK_URL, SUBSTACK_URL.removeprefix('https://'), style='dark_sea_green4 dim')
    print_centered_link('https://cryptadamus.substack.com/', 'Substack', style=SOCIAL_MEDIA_LINK_STYLE)
    print_centered_link('https://universeodon.com/@cryptadamist/115572634993386057', 'Mastodon', style=SOCIAL_MEDIA_LINK_STYLE)
    print_centered_link('https://x.com/Cryptadamist/status/1990866804630036988', 'Twitter', style=SOCIAL_MEDIA_LINK_STYLE)


def print_starred_header(msg: str, num_stars: int = 7, num_spaces: int = 2) -> None:
    stars = '*' * num_stars
    spaces = ' ' * num_spaces
    msg = f"{spaces}{stars} {msg} {stars}{spaces}"
    print_centered(wrap_in_markup_style(msg, TITLE_STYLE))


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


def write_html(output_path: Path) -> None:
    if not args.build:
        logger.warning(f"Not writing HTML because args.build={args.build}.")
        return

    console.save_html(output_path, code_format=CONSOLE_HTML_FORMAT, theme=HTML_TERMINAL_THEME)
    logger.warning(f"Wrote {file_size_str(output_path)} to '{output_path}'")


if args.deep_debug:
    print_json('THEME_STYLES', THEME_STYLES)
