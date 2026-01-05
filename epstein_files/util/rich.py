# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
import json
from os import devnull
from pathlib import Path

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
from epstein_files.util.constant.strings import DEFAULT, EMAIL, NA, OTHER_SITE_LINK_STYLE, QUESTION_MARKS, SiteType
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import FALLBACK_TIMESTAMP, HEADER_ABBREVIATIONS
from epstein_files.util.data import json_safe
from epstein_files.util.env import args
from epstein_files.util.highlighted_group import ALL_HIGHLIGHTS, HIGHLIGHTED_NAMES, EpsteinHighlighter
from epstein_files.util.logging import log_file_write, logger

TITLE_WIDTH = 50
NUM_COLOR_KEY_COLS = 4
NA_TXT = Text(NA, style='dim')
QUESTION_MARK_TXT = Text(QUESTION_MARKS, style='dim')
GREY_NUMBERS = [58, 39, 39, 35, 30, 27, 23, 23, 19, 19, 15, 15, 15]

DEFAULT_NAME_STYLE = 'gray46'
KEY_STYLE='honeydew2 bold'
SECTION_HEADER_STYLE = 'bold white on blue3'
SOCIAL_MEDIA_LINK_STYLE = 'cyan3 bold'
SUBSTACK_POST_LINK_STYLE = 'bright_cyan'
SYMBOL_STYLE = 'grey70'
TITLE_STYLE = 'black on bright_white bold'

HIGHLIGHTED_GROUP_COLOR_KEYS = [
    Text(highlight_group.label.replace('_', ' '), style=highlight_group.style)
    for highlight_group in sorted(HIGHLIGHTED_NAMES, key=lambda hg: hg.label)
]

THEME_STYLES = {
    DEFAULT: 'wheat4',
    TEXT_LINK: 'deep_sky_blue4 underline',
    **{hg.theme_style_name: hg.style for hg in ALL_HIGHLIGHTS},
}

# Instantiate console object
CONSOLE_ARGS = {
    'color_system': '256',
    'highlighter': EpsteinHighlighter(),
    'record': args.build,
    'safe_box': False,
    'theme': Theme(THEME_STYLES),
    'width': args.width,
}

if args.suppress_output:
    logger.warning(f"Suppressing terminal output because args.suppress_output={args.suppress_output}...")
    CONSOLE_ARGS.update({'file': open(devnull, "wt")})

console = Console(**CONSOLE_ARGS)
highlighter = CONSOLE_ARGS['highlighter']


def add_cols_to_table(table: Table, col_names: list[str]) -> None:
    """Left most col will be left justified, rest are center justified."""
    for i, col in enumerate(col_names):
        table.add_column(col, justify='left' if i == 0 else 'center')


def build_highlighter(pattern: str) -> EpsteinHighlighter:
    class TempHighlighter(EpsteinHighlighter):
        """rich.highlighter that finds and colors interesting keywords based on the above config."""
        highlights = EpsteinHighlighter.highlights + [re.compile(fr"(?P<trump>{pattern})", re.IGNORECASE)]

    return TempHighlighter()


def join_texts(txts: list[Text], join: str = ' ', encloser: str = '') -> Text:
    """Join rich.Text objs into one."""
    if encloser:
        if len(encloser) != 2:
            raise ValueError(f"'encloser' arg is '{encloser}' which is not 2 characters long")

        enclose_start, enclose_end = (encloser[0], encloser[1])
    else:
        enclose_start = enclose_end = ''

    txt = Text('')

    for i, link in enumerate(txts):
        txt.append(join if i >= 1 else '').append(enclose_start).append(link).append(enclose_end)

    return txt


def key_value_txt(key: str, value: Text | int | str) -> Text:
    """Generate a Text obj for 'key=value'."""
    if isinstance(value, int):
        value = Text(f"{value}", style='cyan')

    return Text('').append(key, style=KEY_STYLE).append('=', style=SYMBOL_STYLE).append(value)


def parenthesize(msg: str | Text, style: str = '') -> Text:
    txt = Text(msg) if isinstance(msg, str) else msg
    return Text('(', style=style).append(txt).append(')')


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


def print_color_key() -> None:
    color_table = Table(title=f'Rough Guide to Highlighted Colors', show_header=False)
    num_colors = len(HIGHLIGHTED_GROUP_COLOR_KEYS)
    row_number = 0

    for i in range(0, NUM_COLOR_KEY_COLS):
        color_table.add_column(f"color_col_{i}", justify='center')

    while (row_number * NUM_COLOR_KEY_COLS) < num_colors:
        idx = row_number * NUM_COLOR_KEY_COLS
        color_table.add_row(*HIGHLIGHTED_GROUP_COLOR_KEYS[idx:(idx + NUM_COLOR_KEY_COLS)])
        row_number += 1

    print_centered(vertically_pad(color_table))


def print_header(epstein_files: 'EpsteinFiles') -> None:
    not_optimized_msg = f"This site isn't optimized for mobile"

    if not args.all_emails:
        not_optimized_msg += f" but if you get past the header it should be readable"

    console.print(f"{not_optimized_msg}.\n", style='dim')
    print_page_title(width=TITLE_WIDTH)
    print_other_site_link()
    _print_external_links()
    console.line()
    _print_abbreviations_table()
    epstein_files.print_files_summary()
    print_color_key()
    print_centered(f"if you think there's an attribution error or can deanonymize an {UNKNOWN} contact {CRYPTADAMUS_TWITTER}", 'grey46')
    print_centered('note this site is based on the OCR text provided by Congress which is not always the greatest', 'grey23')
    print_centered(f"(thanks to {link_markup('https://x.com/ImDrinknWyn', '@ImDrinknWyn', 'dodger_blue3')} + others for help attributing redacted emails)")
    print_centered_link(ATTRIBUTIONS_URL, "(some explanations of author attributions)", style='magenta')


def print_json(label: str, obj: object, skip_falsey: bool = False) -> None:
    print(obj)

    if isinstance(obj, dict):
        if skip_falsey:
            obj = {k: v for k, v in obj.items() if v}

        obj = json_safe(obj)

    console.line()
    console.print(Panel(label, expand=False))
    console.print_json(json.dumps(obj, sort_keys=True), indent=4)
    console.line()


def print_numbered_list_of_emailers(_list: list[str | None], epstein_files = None) -> None:
    """Add the first emailed_at timestamp for each emailer if 'epstein_files' provided."""
    current_year = 1990
    current_year_month = current_year * 12
    grey_idx = 0
    console.line()

    for i, name in enumerate(_list):
        indent = '   ' if i < 9 else ('  ' if i < 99 else ' ')
        txt = Text((indent) + F"   {i + 1}. ", style=DEFAULT_NAME_STYLE)

        if epstein_files:
            earliest_email_date = (epstein_files.earliest_email_at(name) or FALLBACK_TIMESTAMP).date()
            year_months = (earliest_email_date.year * 12) + earliest_email_date.month

            # Color year rollovers more brightly
            if current_year != earliest_email_date.year:
                grey_idx = 0
            elif current_year_month != year_months:
                grey_idx = ((current_year_month - 1) % 12) + 1

            current_year_month = year_months
            current_year = earliest_email_date.year
            txt.append(escape(f"[{earliest_email_date}] "), style=f"grey{GREY_NUMBERS[grey_idx]}")

        txt.append(highlighter(name or UNKNOWN))

        if epstein_files:
            num_days_in_converation = epstein_files.email_conversation_length_in_days(name)
            msg = f" ({len(epstein_files.emails_for(name))} emails over {num_days_in_converation:,} days)"
            txt.append(msg, style=f'dim italic')

        console.print(txt)

    console.line()


def print_other_site_link(is_header: bool = True) -> None:
    """Print a link to the emails site if we're building text messages site and vice versa."""
    site_type: SiteType = EMAIL if args.all_emails else TEXT_MESSAGE

    if is_header:
        print_starred_header(f"This is the Epstein {site_type.title()}s site", num_spaces=4, num_stars=14)

    other_site_type: SiteType = TEXT_MESSAGE if site_type == EMAIL else EMAIL
    other_site_msg = "another site for" + (' all of' if other_site_type == EMAIL else '')
    other_site_msg += f" Epstein's {other_site_type}s also generated by this code"
    markup_msg = link_markup(SITE_URLS[other_site_type], other_site_msg, OTHER_SITE_LINK_STYLE)
    print_centered(parenthesize(Text.from_markup(markup_msg)), style='bold')
    word_count_link = link_text_obj(WORD_COUNT_URL, 'site showing the most frequently used words in these communiques', OTHER_SITE_LINK_STYLE)
    print_centered(parenthesize(word_count_link))
    metadata_link = link_text_obj(JSON_METADATA_URL, 'metadata with author attribution explanations', OTHER_SITE_LINK_STYLE)
    print_centered(parenthesize(metadata_link))


def print_page_title(expand: bool = True, width: int | None = None) -> None:
    title_panel = Panel(Text(PAGE_TITLE, justify='center'), expand=expand, style=TITLE_STYLE, width=width)
    console.print(Align.center(vertically_pad(title_panel)))
    print_social_media_links()
    console.line(2)


def print_panel(msg: str, style: str = 'black on white', padding: tuple | None = None, centered: bool = False) -> None:
    _padding: list[int] = list(padding or [0, 0, 0, 0])
    _padding[2] += 1  # Bottom pad
    panel = Panel(Text.from_markup(msg, justify='center'), width=70, style=style)
    actual_padding: tuple[int, int, int, int] = tuple(_padding)

    if centered:
        console.print(Align.center(Padding(panel, actual_padding)))
    else:
        console.print(Padding(panel, actual_padding))


def print_section_header(msg: str, style: str = SECTION_HEADER_STYLE, is_centered: bool = False) -> None:
    panel = Panel(Text(msg, justify='center'), expand=True, padding=(1, 1), style=style)
    panel = Align.center(panel) if is_centered else panel
    console.print(Padding(panel, (3, 0, 1, 0)))


def print_social_media_links() -> None:
    print_centered_link(SUBSTACK_URL, "I Made Epstein's Text Messages Great Again (And You Should Read Them)", style=f'{SUBSTACK_POST_LINK_STYLE} bold')
    print_centered_link(SUBSTACK_URL, SUBSTACK_URL.removeprefix('https://'), style=f'{SUBSTACK_POST_LINK_STYLE} dim')

    social_links = [
        link_text_obj('https://x.com/Cryptadamist/status/1990866804630036988', '@cryptadamist', style=SOCIAL_MEDIA_LINK_STYLE),
        link_text_obj('https://cryptadamus.substack.com/', 'substack', style=SOCIAL_MEDIA_LINK_STYLE),
        link_text_obj('https://universeodon.com/@cryptadamist/115572634993386057', 'mastodon', style=SOCIAL_MEDIA_LINK_STYLE),
    ]

    print_centered(join_texts(social_links, join='     ', encloser='[]'))


def print_starred_header(msg: str, num_stars: int = 7, num_spaces: int = 2, style: str = TITLE_STYLE) -> None:
    stars = '*' * num_stars
    spaces = ' ' * num_spaces
    msg = f"{spaces}{stars} {msg} {stars}{spaces}"
    print_centered(wrap_in_markup_style(msg, style))


def vertically_pad(obj: RenderableType, amount: int = 1) -> Padding:
    return Padding(obj, (amount, 0, amount, 0))


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

    console.save_html(str(output_path), code_format=CONSOLE_HTML_FORMAT, theme=HTML_TERMINAL_THEME)
    log_file_write(output_path)


def _print_abbreviations_table() -> None:
    table = Table(title="Abbreviations Used Frequently In These Conversations", header_style="bold", show_header=False)
    table.add_column("Abbreviation", justify="center", style='bold')
    table.add_column("Translation", style="white", justify="center")

    for k, v in HEADER_ABBREVIATIONS.items():
        table.add_row(highlighter(k), v)

    console.print(Align.center(vertically_pad(table)))


def _print_external_links() -> None:
    console.line()
    print_starred_header('External Links', num_stars=0, num_spaces=20, style=f"italic")
    presser_link = link_text_obj(OVERSIGHT_REPUBLICANS_PRESSER_URL, 'Official Oversight Committee Press Release')
    raw_docs_link = join_texts([link_text_obj(RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL, 'raw files', style=f"{ARCHIVE_LINK_COLOR} dim")], encloser='()')
    print_centered(join_texts([presser_link, raw_docs_link]))
    print_centered(link_markup(JMAIL_URL, JMAIL) + " (read His Emails via Gmail interface)")
    print_centered(link_markup(COFFEEZILLA_ARCHIVE_URL, 'Archive Of Epstein Materials') + " (Coffeezilla)")
    print_centered(link_markup(COURIER_NEWSROOM_ARCHIVE_URL, 'Searchable Archive') + " (Courier Newsroom)")
    print_centered(link_markup(EPSTEINIFY_URL) + " (raw document images)")
    print_centered(link_markup(EPSTEIN_WEB_URL) + " (character summaries)")


# if args.deep_debug:
#     print_json('THEME_STYLES', THEME_STYLES)
