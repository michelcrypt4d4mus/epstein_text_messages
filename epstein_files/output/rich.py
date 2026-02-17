# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
import json
from copy import deepcopy
from datetime import datetime
from os import devnull
from pathlib import Path
from typing import Mapping, Sequence

from rich import box
from rich.align import Align
from rich.console import Console, Group, RenderableType
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from epstein_files.output.epstein_highlighter import EpsteinHighlighter
from epstein_files.output.highlight_config import HIGHLIGHT_GROUPS
from epstein_files.util.constant.html import CONSOLE_HTML_FORMAT, HTML_TERMINAL_THEME, PAGE_TITLE
from epstein_files.util.constant.names import UNKNOWN
from epstein_files.util.constant.output_files import GH_PROJECT_URL, SITE_DESCRIPTIONS, parenthesize
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import HEADER_ABBREVIATIONS
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import json_safe, sort_dict, without_falsey
from epstein_files.util.helpers.file_helper import log_file_write
from epstein_files.util.helpers.link_helper import link_markup, link_text_obj
from epstein_files.util.helpers.string_helper import quote
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
SITE_GLOSSARY_MSG = f"These pages include the following views of the underlying collection of Epstein's files:"
YOU_ARE_HERE = Text('«').append('you are here', style='bold khaki1 blink').append('»')

DATASET_DESCRIPTION_STYLE = 'gray74'
INFO_STYLE = 'white dim italic'
KEY_STYLE = 'dim'
KEY_STYLE_ALT = 'light_steel_blue3'
LAST_TIMESTAMP_STYLE = 'wheat4'
OTHER_PAGE_MSG_STYLE = 'gray78 dim'
PATH_STYLE = 'deep_pink3'
STR_VAL_STYLE = 'cornsilk1 italic'
STR_VAL_STYLE_ALT = 'light_yellow3 italic'
SECTION_HEADER_STYLE = 'bold white on blue3'
SOCIAL_MEDIA_LINK_STYLE = 'pale_turquoise4'
SUBSTACK_POST_LINK_STYLE = 'bright_cyan'
SYMBOL_STYLE = 'grey70'
TABLE_BORDER_STYLE = 'grey46'
TABLE_TITLE_STYLE = f"gray54 italic"
TITLE_STYLE = 'black on bright_white bold'

OTHER_SITE_LINK_STYLE = 'dark_goldenrod'

DEFAULT_TABLE_KWARGS = {
    'border_style': TABLE_BORDER_STYLE,
    'caption_style': 'navajo_white3 dim italic',
    'header_style': "bold",
    'title_style': TABLE_TITLE_STYLE,
}

HIGHLIGHTED_GROUP_COLOR_KEYS = [
    Text(highlight_group.label.replace('_', ' '), style=highlight_group.style)
    for highlight_group in sorted(HIGHLIGHT_GROUPS, key=lambda hg: hg.label)
]

THEME_STYLES = {
    DEFAULT: 'wheat4',
    TEXT_LINK: 'deep_sky_blue4 underline',
    **{hg.theme_style_name: hg.style for hg in HIGHLIGHT_GROUPS},
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


def bool_txt(b: bool | None) -> Text:
    if b is False:
        return Text(str(b), style='bright_red bold italic')
    elif b is True:
        return Text(str(b), style='bright_green bold italic')
    else:
        return Text(str(b), style='dim italic')


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


def indent_txt(txt: str | Text, spaces: int = 4, prefix: str = '') -> Text:
    indent = Text(' ' * spaces).append(prefix)
    return indent + Text(f"\n{indent}").join(txt.split('\n'))


def join_texts(txts: Sequence[str | Text], join: str = ' ', encloser: str = '', encloser_style: str = 'wheat4') -> Text:
    """Join rich.Text objs into one."""
    if encloser:
        if len(encloser) != 2:
            raise ValueError(f"'encloser' arg is '{encloser}' which is not 2 characters long")

        enclose_start, enclose_end = (encloser[0], encloser[1])
    else:
        enclose_start = enclose_end = ''

    txt = Text('')

    for i, _txt in enumerate(without_falsey(txts)):
        txt.append(join if i >= 1 else '').append(enclose_start, style=encloser_style)
        txt.append(_txt).append(enclose_end, style=encloser_style)

    return txt


def prefix_with(txt: list[str] | list[Text] | Text | str, pfx: str, pfx_style: str = '', indent: str | int = '') -> Text:
    indent = indent * ' ' if isinstance(indent, int) else indent

    lines = [
        Text('').append(f"{indent}{pfx} ", style=pfx_style).append(line)
        for line in (txt.split('\n') if isinstance(txt, (Text, str)) else txt)
    ]

    return Text('\n').join(lines)


def print_centered(obj: RenderableType, style: str = '') -> None:
    console.print(Align.center(obj), highlight=False, style=style)


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
    links = {site_type: SiteType.link_txt(site_type) for site_type in SITE_DESCRIPTIONS.keys()}

    def site_link_line(site_type: SiteType, bulleted_link: Text) -> Text:
        you_are_here = YOU_ARE_HERE if site_type == args._site_type else ''
        return Text('➱ ').append(bulleted_link).append(' ').append(you_are_here)

    # Print the stuff
    print_page_title(width=TITLE_WIDTH)
    sites_txt = Text('').append(SITE_GLOSSARY_MSG, style='wheat4 bold').append('\n\n')
    links_txts = [site_link_line(site_type, link) for site_type, link in links.items()]
    max_link_len = max(len(link.plain) for link in links.values())
    num_link_indent_spaces = max(2, int((len(SITE_GLOSSARY_MSG) - max_link_len) / 2)) - 2
    sites_txt.append(indent_txt(join_texts(links_txts, '\n'), num_link_indent_spaces))
    print_centered(Panel(sites_txt, border_style='dim', padding=(1, 5)))
    console.line()
    print_starred_header('Not All Epstein Files Are Here!', num_spaces=9 if args.all_emails else 6, num_stars=14)
    print_centered(f"This dataset includes everything from the {HOUSE_OVERSIGHT_TRANCHE}", style=DATASET_DESCRIPTION_STYLE)
    print_centered(f"as well as a curated selection of the {DOJ_2026_TRANCHE}.\n", style=DATASET_DESCRIPTION_STYLE)

    if args._site_type == SiteType.CURATED:
        _print_section_links()


def print_title_page_tables(epstein_files: 'EpsteinFiles') -> None:
    """Bottom half of the title page."""
    _print_external_links()
    console.line()
    _print_abbreviations_table()
    print_centered(epstein_files.overview_table())
    console.line()
    print_color_key()
    print_centered(f"(if you think there's an attribution error or can deanonymize an {UNKNOWN} contact {CRYPTADAMUS_TWITTER})", 'grey46')
    print_centered(parenthesize('note this site is based on the government provided OCR text which is not always the greatest'), 'grey23')
    print_centered(f"(thanks to {link_markup('https://x.com/ImDrinknWyn', '@ImDrinknWyn', 'dodger_blue3')} + others for help attributing redacted emails)")
    print_centered_link(SiteType.get_url(SiteType.JSON_METADATA), "(explanations of author attributions)", style='magenta')


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
    if args._site_type == SiteType.CURATED:
        txt = THE_OTHER_PAGE_TXT + Text(f' is uncurated and has all {len(epstein_files.emails):,} emails')
        txt.append(f" and {len(epstein_files.other_files):,} unclassifiable files")
    else:
        txt = THE_OTHER_PAGE_TXT + (f' displays a curated collection of emails and')
        txt.append(" unclassifiable files of particular interest")

    print_centered(parenthesize(txt), style=OTHER_PAGE_MSG_STYLE)
    chrono_emails_link = link_text_obj(SiteType.get_url(SiteType.CHRONOLOGICAL_EMAILS), 'a page', style='light_slate_grey bold')
    chrono_emails_txt = Text(f"there's also ").append(chrono_emails_link)
    chrono_emails_txt.append(' with all the emails in chronological order')
    print_centered(parenthesize(chrono_emails_txt), style=OTHER_PAGE_MSG_STYLE)


def print_page_title(expand: bool = True, width: int | None = None) -> None:
    warning = f"This page was generated by {link_markup('https://pypi.org/project/rich/', 'rich')}."
    print_centered(f"{warning} It is not optimized for mobile.", style='dim')
    title_panel = Panel(Text('The Epstein Files', justify='center'), expand=expand, style=TITLE_STYLE, width=width)
    print_centered(vertically_pad(title_panel))
    _print_social_media_links()
    console.line()


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


def cfg_table(cfg: 'DocCfg') -> Padding:
    props = cfg.important_props
    props.pop('id')
    props_table = styled_dict(props, sep=': ')
    return Padding(indent_txt(props_table, 12), (0, 0, 1, 0))


def quote_txt(t: Text | str, try_double_quote_first: bool = False, style: str = '') -> Text:
    if try_double_quote_first:
        quote_char = '"' if '"' not in t else "'"
    else:
        quote_char = "'" if "'" not in t else '"'

    return Text(quote_char, style=style).append(t).append(quote_char)


def styled_dict(
    d: Mapping[str, bool | datetime | str | Path | Text | None],
    key_style: str = KEY_STYLE,
    sep: str = '=',
    sort_fields: bool = True,
    min_indent: int = 20,
) -> Text:
    """Turn a dict into a colored representation."""
    key_lengths = [len(k) for k in d.keys()] + [min_indent]

    return Text('\n').join([
        styled_key_value(k, v, key_style=key_style, indent=max(key_lengths) + 3, sep=sep)
        for k, v in (sort_dict(d) if sort_fields else d.items())
    ])


def styled_key_value(
    key: str,
    val: bool | datetime | int | str | Path | Text | None,
    key_style: str = KEY_STYLE,
    indent: int = 0,
    sep='='
) -> Text:
    """Generate `Text` for 'key=value'."""
    if '.' in key and key_style == KEY_STYLE:
        key_style = KEY_STYLE_ALT

    if val is None:
        val_txt = Text('None', style='dim italic')
    elif isinstance(val, Text):
        val_txt = val
    elif isinstance(val, list):
        val_txt = highlighter(json.dumps(val))
    elif isinstance(val, bool):
        val_txt = bool_txt(val)
    elif isinstance(val, datetime):
        val_txt = Text(str(val), style=TIMESTAMP_STYLE)
    else:
        val_txt = None
        val_style = ''

        if isinstance(val, int):
            val = str(val)
            val_style = 'cyan'
        elif isinstance(val, Path):
            val = val = f"'{val}'"
            val_style = PATH_STYLE
        elif isinstance(val, str):
            if val.startswith('http'):
                val_style = ARCHIVE_LINK_UNDERLINE
            elif key.endswith('category') or key == AUTHOR:
                val_txt = highlighter(val)
            elif key.endswith('filename'):
                val_style = PATH_STYLE
            elif key.endswith('style'):
                val_style = f"{val} bold"
            elif key.endswith('_type'):
                val_style = 'light_slate_gray bold'
            elif key.endswith('id'):
                val_style = 'cyan'
            else:
                val_style = STR_VAL_STYLE_ALT if '.' in key else STR_VAL_STYLE
                val_txt = quote_txt(highlighter(val), style=val_style)

        val_txt = val_txt or Text(str(val), style=val_style or 'bright_white')

    txt = Text('').append(f"{key:>{indent}}", style=key_style)
    txt.append(sep, style=SYMBOL_STYLE).append(val_txt)
    return txt


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


SECTION_LINK_MSG = 'jump to different sections of this page'
from enum import auto, StrEnum
from rich.segment import Segment

class PageSections(StrEnum):
    TEXT_MESSAGES = auto()
    EMAILS = auto()
    OTHER_FILES = auto()

SECTION_ANCHORS = {
    PageSections.TEXT_MESSAGES: 'Selections from His Text Messages',
    PageSections.EMAILS: 'Selections from His Emails',
    PageSections.OTHER_FILES: 'Selected Files That Are Neither Emails Nor',
}

SECTION_LINKS = [
    link_text_obj(internal_link_url(anchor), section_name, 'indian_red')
    for section_name, anchor in SECTION_ANCHORS.items()
]

def _print_section_links() -> None:
    sections_container = Table(box=box.ROUNDED, show_header=False, collapse_padding=True, show_edge=False, style='gray23')
    sections_container.add_column('msg', width=19, style='dim', justify='right')
    sections_container.add_column('link', justify='left')
    links_table = Table(show_header=False, collapse_padding=True, show_edge=False, style='gray23')
    links_table.add_column('link', justify='left')

    for link in SECTION_LINKS:
        links_table.add_row(link)

    sections_container.add_row(SECTION_LINK_MSG, links_table)
    print_centered('-' * 50, style='grey15')
    print_centered(sections_container)
    print_centered('-' * 50, style='grey15')

    # print_centered('jump to different sections of this page:')
    # for link in section_links:
    #     print_centered(link)


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
