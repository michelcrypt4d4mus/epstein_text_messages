# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
import json
from copy import deepcopy
from os import devnull
from pathlib import Path

from rich.align import Align
from rich.console import Console, Group, RenderableType
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from epstein_files.util.constant.html import CONSOLE_HTML_FORMAT, HTML_TERMINAL_THEME, PAGE_TITLE
from epstein_files.util.constant.names import UNKNOWN
from epstein_files.util.constant.strings import DEFAULT, EMAIL, NA, TEXT_MESSAGE
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import HEADER_ABBREVIATIONS
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import json_safe
from epstein_files.util.helpers.file_helper import log_file_write
from epstein_files.util.highlighted_group import ALL_HIGHLIGHTS, HIGHLIGHTED_NAMES, EpsteinHighlighter
from epstein_files.util.logging import logger

TITLE_WIDTH = 50
SUBTITLE_WIDTH = 110
NUM_COLOR_KEY_COLS = 6
NA_TXT = Text(NA, style='dim')
SKIPPED_FILE_MSG_PADDING = (0, 0, 0, 4)
SUBTITLE_PADDING = (2, 0, 1, 0)
GREY_NUMBERS = [58, 39, 39, 35, 30, 27, 23, 23, 19, 19, 15, 15, 15]
VALID_GREYS = [0, 3, 7, 11, 15, 19, 23, 27, 30, 35, 37, 39, 42, 46, 50, 53, 54, 58, 62, 63, 66, 69, 70, 74, 78, 82, 84, 85, 89, 93]
DOJ_PAGE_LINK_MSG = 'WIP page with documents from the Epstein Files Transparency Act'

INFO_STYLE = 'white dim italic'
KEY_STYLE = 'honeydew2'
LAST_TIMESTAMP_STYLE = 'wheat4'
OTHER_PAGE_MSG_STYLE = 'gray78 dim'
SECTION_HEADER_STYLE = 'bold white on blue3'
SOCIAL_MEDIA_LINK_STYLE = 'pale_turquoise4'
SUBSTACK_POST_LINK_STYLE = 'bright_cyan'
SYMBOL_STYLE = 'grey70'
TABLE_BORDER_STYLE = 'grey46'
TABLE_TITLE_STYLE = f"gray54 italic"
TITLE_STYLE = 'black on bright_white bold'

AUX_SITE_LINK_STYLE = 'dark_orange3'
OTHER_SITE_LINK_STYLE = 'dark_goldenrod'

DEFAULT_TABLE_KWARGS = {
    'border_style': TABLE_BORDER_STYLE,
    'caption_style': 'navajo_white3 dim italic',
    'header_style': "bold",
    'title_style': TABLE_TITLE_STYLE,
}

HIGHLIGHTED_GROUP_COLOR_KEYS = [
    Text(highlight_group.label.replace('_', ' '), style=highlight_group.style)
    for highlight_group in sorted(HIGHLIGHTED_NAMES, key=lambda hg: hg.label)
]

THEME_STYLES = {
    DEFAULT: 'wheat4',
    TEXT_LINK: 'deep_sky_blue4 underline',
    **{hg.theme_style_name: hg.style for hg in ALL_HIGHLIGHTS},
}

RAINBOW = [
    'royal_blue1',
    'medium_purple',
    'light_coral',
    'light_slate_gray',
    'dark_goldenrod',
    'wheat4',
    'white',
    'medium_orchid',
    'deep_pink1',
    'navajo_white1',
]

# Instantiate console object
CONSOLE_ARGS = {
    'color_system': '256',
    'highlighter': EpsteinHighlighter(),
    'record': args.build,
    'safe_box': True,
    'theme': Theme(THEME_STYLES),
    'width': args.width,
}

if args.suppress_output:
    logger.warning(f"Suppressing terminal output because args.suppress_output={args.suppress_output}...")
    CONSOLE_ARGS.update({'file': open(devnull, "wt")})

console = Console(**CONSOLE_ARGS)
highlighter = CONSOLE_ARGS['highlighter']


def add_cols_to_table(table: Table, cols: list[str | dict], justify: str = 'center') -> None:
    """Left most col will be left justified, rest are center justified."""
    for i, col in enumerate(cols):
        col_justify = 'left' if i == 0 else justify

        if isinstance(col, dict):
            col_name = col['name']
            col_kwargs = deepcopy(col)
            col_kwargs['justify'] = col_kwargs.get('justify', col_justify)
            del col_kwargs['name']
        else:
            col_name = col
            col_kwargs = {'justify': col_justify}

        table.add_column(col_name, **col_kwargs)


def build_highlighter(pattern: str) -> EpsteinHighlighter:
    class TempHighlighter(EpsteinHighlighter):
        """rich.highlighter that finds and colors interesting keywords based on the above config."""
        highlights = EpsteinHighlighter.highlights + [re.compile(fr"(?P<trump>{pattern})", re.IGNORECASE)]

    return TempHighlighter()


def build_table(title: str | Text | None, cols: list[str | dict] | None = None, **kwargs) -> Table:
    table = Table(title=title, **{**DEFAULT_TABLE_KWARGS, **kwargs})

    if cols:
        add_cols_to_table(table, cols)

    return table


def join_texts(txts: list[Text], join: str = ' ', encloser: str = '', encloser_style: str = 'wheat4') -> Text:
    """Join rich.Text objs into one."""
    if encloser:
        if len(encloser) != 2:
            raise ValueError(f"'encloser' arg is '{encloser}' which is not 2 characters long")

        enclose_start, enclose_end = (encloser[0], encloser[1])
    else:
        enclose_start = enclose_end = ''

    txt = Text('')

    for i, _txt in enumerate(txts):
        txt.append(join if i >= 1 else '').append(enclose_start, style=encloser_style)
        txt.append(_txt).append(enclose_end, style=encloser_style)

    return txt


def parenthesize(msg: str | Text, style: str = '') -> Text:
    txt = Text(msg) if isinstance(msg, str) else msg
    return Text('(', style=style).append(txt).append(')')


def prefix_with(txt: list[str] | list[Text] | Text | str, pfx: str, pfx_style: str = '', indent: str | int = '') -> Text:

    indent = indent * ' ' if isinstance(indent, int) else indent

    lines = [
        Text('').append(f"{indent}{pfx} ", style=pfx_style).append(line)
        for line in (txt.split('\n') if isinstance(txt, (Text, str)) else txt)
    ]


    return Text('\n').join(lines)


def print_centered(obj: RenderableType, style: str = '') -> None:
    console.print(Align.center(obj), style=style)


def print_centered_link(url: str, link_text: str, style: str | None = None) -> None:
    print_centered(link_markup(url, link_text, style or ARCHIVE_LINK_COLOR))


def print_color_key() -> None:
    color_table = build_table('Rough Guide to Highlighted Colors', show_header=False)
    num_colors = len(HIGHLIGHTED_GROUP_COLOR_KEYS)
    row_number = 0

    for i in range(0, NUM_COLOR_KEY_COLS):
        color_table.add_column(f"color_col_{i}", justify='center')

    while (row_number * NUM_COLOR_KEY_COLS) < num_colors:
        idx = row_number * NUM_COLOR_KEY_COLS
        color_table.add_row(*HIGHLIGHTED_GROUP_COLOR_KEYS[idx:(idx + NUM_COLOR_KEY_COLS)])
        row_number += 1

    print_centered(vertically_pad(color_table))


def print_title_page_header() -> None:
    """Top half of the title page."""
    print_page_title(width=TITLE_WIDTH)
    site_type = EMAIL if (args.all_emails or args.email_timeline) else TEXT_MESSAGE
    title = f"This is the "

    if args.output_doj_files:
        title += "DOJ 2026-01-30 Document Dump"
    else:
        title += ('Chronological ' if args.email_timeline else '') + f"Epstein {site_type.title()}s Page"

    print_starred_header(title, num_spaces=9 if args.all_emails else 6, num_stars=14)
    #print_centered(f"This page contains all of the text messages and a curated selection of emails and other files.", style='gray74')
    print_centered(f"These documents come from the Nov. 2025 House Oversight Committee release.\n", style='gray74')
    other_site_msg = "another page with" + (' all of' if other_site_type() == EMAIL else '')
    other_site_msg += f" Epstein's {other_site_type()}s also generated by this code"

    links = [
        Text.from_markup(link_markup(other_site_url(), other_site_msg, f"{OTHER_SITE_LINK_STYLE} bold")),
        Text.from_markup(link_markup(DOJ_2026_URL, DOJ_PAGE_LINK_MSG, f"{OTHER_SITE_LINK_STYLE} bold")),
        link_text_obj(WORD_COUNT_URL, 'most frequently used words in the emails and texts', AUX_SITE_LINK_STYLE),
        link_text_obj(JSON_METADATA_URL, 'author attribution explanations', AUX_SITE_LINK_STYLE),
        link_text_obj(JSON_FILES_URL, "epstein's json files", AUX_SITE_LINK_STYLE),
    ]

    for link in links:
        print_centered(parenthesize(link))


def print_title_page_tables(epstein_files: 'EpsteinFiles') -> None:
    """Bottom half of the title page."""
    _print_external_links()
    console.line()
    _print_abbreviations_table()
    print_centered(epstein_files.overview_table())
    console.line()
    print_color_key()
    print_centered(f"if you think there's an attribution error or can deanonymize an {UNKNOWN} contact {CRYPTADAMUS_TWITTER}", 'grey46')
    print_centered('note this site is based on the OCR text provided by Congress which is not always the greatest', 'grey23')
    print_centered(f"(thanks to {link_markup('https://x.com/ImDrinknWyn', '@ImDrinknWyn', 'dodger_blue3')} + others for help attributing redacted emails)")
    print_centered_link(JSON_METADATA_URL, "(explanations of author attributions)", style='magenta')


def print_json(label: str, obj: object, skip_falsey: bool = False) -> None:
    if isinstance(obj, dict):
        if skip_falsey:
            obj = {k: v for k, v in obj.items() if v}

        obj = json_safe(obj)

    console.line()
    console.print(Panel(label, expand=False))
    console.print_json(json.dumps(obj, sort_keys=True), indent=4)
    console.line()


def print_other_page_link(epstein_files: 'EpsteinFiles') -> None:
    if other_site_type() == EMAIL:
        txt = THE_OTHER_PAGE_TXT + Text(f' is uncurated and has all {len(epstein_files.emails):,} emails')
        txt.append(f" and {len(epstein_files.other_files)} unclassifiable files")
    else:
        txt = THE_OTHER_PAGE_TXT + (f' displays a limited collection of emails and')
        txt.append(" unclassifiable files of particular interest")

    print_centered(parenthesize(txt), style=OTHER_PAGE_MSG_STYLE)
    chrono_emails_markup = link_text_obj(CHRONOLOGICAL_EMAILS_URL, 'a page', style='light_slate_grey bold')
    chrono_emails_txt = Text(f"there's also ").append(chrono_emails_markup)
    chrono_emails_txt.append(' with all the emails in chronological order')
    print_centered(parenthesize(chrono_emails_txt), style=OTHER_PAGE_MSG_STYLE)


def print_page_title(expand: bool = True, width: int | None = None) -> None:
    warning = f"This page was generated by {link_markup('https://pypi.org/project/rich/', 'rich')}."
    print_centered(f"{warning} It is not optimized for mobile.", style='dim')
    title_panel = Panel(Text(PAGE_TITLE, justify='center'), expand=expand, style=TITLE_STYLE, width=width)
    print_centered(vertically_pad(title_panel))
    _print_social_media_links()
    console.line(2)


def print_subtitle_panel(msg: str, style: str = 'black on white') -> None:
    panel = Panel(Text.from_markup(msg, justify='center'), width=SUBTITLE_WIDTH, style=style)
    print_centered(Padding(panel, SUBTITLE_PADDING))


def print_section_header(msg: str, style: str = SECTION_HEADER_STYLE, is_centered: bool = False) -> None:
    panel = Panel(Text(msg, justify='center'), expand=True, padding=(1, 1), style=style)
    panel = Align.center(panel) if is_centered else panel
    console.print(Padding(panel, (3, 5, 1, 5)))


def print_starred_header(msg: str, num_stars: int = 7, num_spaces: int = 2, style: str = TITLE_STYLE) -> None:
    stars = '*' * num_stars
    spaces = ' ' * num_spaces
    msg = f"{spaces}{stars} {msg} {stars}{spaces}"
    print_centered(wrap_in_markup_style(msg, style))


def styled_key_value(
    key: str,
    val: int | str | Path | Text,
    key_style: str = KEY_STYLE,
    indent: int = 0,
    sep='='
) -> Text:
    """Generate `Text` for 'key=value'."""
    if isinstance(val, Text):
        val_txt = val
    else:
        val_style: str = 'bright_white bold'

        if isinstance(val, int):
            val = str(val)
            val_style = 'cyan'
        elif isinstance(val, str) and val.startswith('http'):
            val_style = ARCHIVE_LINK_UNDERLINE
        elif isinstance(val, Path):
            val = val = f"'{val}'"
            val_style = 'deep_pink3'

        val_txt = Text(str(val), style=val_style)

    txt = Text('').append(f"{key:>{indent}}", style=key_style)
    return txt.append(sep, style=SYMBOL_STYLE).append(val_txt)


def styled_dict(d: dict[str, str | Path | Text], key_style: str = KEY_STYLE, sep: str = '=') -> Text:
    """Turn a dict into a colored representation."""
    key_column_width = max(len(k) for k in d.keys()) + 3

    return Text('\n').join([
        styled_key_value(k, v, key_style=key_style, indent=key_column_width, sep=sep)
        for k, v in d.items()
    ])


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


def write_html(output_path: Path | None) -> None:
    if not output_path:
        logger.warning(f"Not writing HTML because args.build={args.build}.")
        return

    console.save_html(str(output_path), clear=False, code_format=CONSOLE_HTML_FORMAT, theme=HTML_TERMINAL_THEME)
    log_file_write(output_path)

    if args.write_txt:
        txt_path = f"{output_path}.txt"
        console.save_text(txt_path)
        log_file_write(txt_path)


def _print_abbreviations_table() -> None:
    table = build_table(title="Abbreviations Used Frequently In These Conversations", show_header=False)
    table.add_column("Abbreviation", justify="center", style='bold')
    table.add_column("Translation", justify="center", min_width=62, style="white")

    for k, v in HEADER_ABBREVIATIONS.items():
        table.add_row(highlighter(k), v)

    console.print(Align.center(vertically_pad(table)))


def _print_external_links() -> None:
    console.line()
    print_centered(Text('External Links', style=TABLE_TITLE_STYLE))
    presser_link = link_text_obj(OVERSIGHT_REPUBLICANS_PRESSER_URL, 'Official Oversight Committee Press Release')
    raw_docs_link = link_text_obj(RAW_OVERSIGHT_DOCS_GOOGLE_DRIVE_URL, 'raw files', style=ARCHIVE_ALT_LINK_STYLE)
    raw_docs_link = join_texts([raw_docs_link], encloser='()')
    print_centered(join_texts([presser_link, raw_docs_link]))
    doj_docs_link = link_text_obj(DOJ_2026_URL, 'Epstein Files Transparency Act Disclosures')
    doj_search_link = join_texts([link_text_obj(DOJ_SEARCH_URL, 'search', style=ARCHIVE_ALT_LINK_STYLE)], encloser='()')
    print_centered(join_texts([doj_docs_link, doj_search_link]))
    print_centered(link_markup(JMAIL_URL, JMAIL) + " (read His Emails via Gmail interface)")
    print_centered(link_markup(EPSTEIN_DOCS_URL) + " (searchable archive)")
    print_centered(link_markup(EPSTEINIFY_URL) + " (raw document images)")
    print_centered(link_markup(EPSTEIN_WEB_URL) + " (character summaries)")
    print_centered(link_markup(EPSTEIN_MEDIA_URL) + " (raw document images)")


def _print_social_media_links() -> None:
    print_centered_link(
        SUBSTACK_URL,
        "I Made Epstein's Text Messages Great Again (And You Should Read Them)",
        style=f'{SUBSTACK_POST_LINK_STYLE} bold'
    )

    print_centered_link(SUBSTACK_URL, SUBSTACK_URL.removeprefix('https://'), style=f'{SUBSTACK_POST_LINK_STYLE} dim')

    social_links = [
        link_text_obj('https://universeodon.com/@cryptadamist/115572634993386057', '@mastodon', style=SOCIAL_MEDIA_LINK_STYLE),
        link_text_obj(SUBSTACK_URL, '@substack', style=SOCIAL_MEDIA_LINK_STYLE),
        link_text_obj('https://x.com/Cryptadamist/status/1990866804630036988', '@twitter', style=SOCIAL_MEDIA_LINK_STYLE),
        link_text_obj(GH_PROJECT_URL, '@github', style=SOCIAL_MEDIA_LINK_STYLE)
    ]

    print_centered(join_texts(social_links, join='  /  '))#, encloser='()'))#, encloser='‹›'))


if args.colors_only:
    print_json('THEME_STYLES', THEME_STYLES)
