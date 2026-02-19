"""
Methods that print the title page with all the links etc.
"""
# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
from rich import box
from rich.align import Align
from rich.console import Console, Group, RenderableType
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from epstein_files.output.layout_elements.demi_table import build_demi_table
from epstein_files.output.highlight_config import HIGHLIGHTED_NAMES
from epstein_files.output.rich import *
from epstein_files.output.site.sites import SECTION_ANCHORS
from epstein_files.output.site.site_config import MOBILE_WARNING
from epstein_files.util.constant.names import UNKNOWN
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import HEADER_ABBREVIATIONS
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.link_helper import SUBSTACK_POST_LINK_STYLE, link_markup, link_text_obj, parenthesize
from epstein_files.util.helpers.string_helper import starred_header
from epstein_files.util.logging import logger

DATASET_DESCRIPTION_STYLE = 'gray74'
OTHER_PAGE_MSG_STYLE = 'gray78 dim'
STR_VAL_STYLE = 'cornsilk1 italic'
STR_VAL_STYLE_ALT = 'light_yellow3 italic'
SECTION_HEADER_STYLE = 'bold black on color(146)'

SITE_GLOSSARY_MSG = f"The following views of the underlying selection of Epstein Files are available:"
YOU_ARE_HERE = Text('«').append('you are here', style='bold khaki1 blink').append('»')
SECTION_LINK_MSG = 'jump to a different section of this page'
SUBTITLE_WIDTH = 110
TITLE_WIDTH = 50

# label of the HighlightedNames objects colors with the style of that same HighlightedNames
COLOR_KEYS = [
    Text(highlight_group.label.replace('_', ' '), style=highlight_group.style)
    for highlight_group in sorted(HIGHLIGHTED_NAMES, key=lambda hg: hg.label)
]

SECTION_LINKS = [
    link_text_obj(internal_link_url(anchor), section_name, 'indian_red')
    for section_name, anchor in SECTION_ANCHORS.items()
]


def print_color_key() -> None:
    color_table = build_table('Rough Guide to Highlighted Colors', show_header=False)
    num_colors = len(COLOR_KEYS)
    row_number = 0

    for i in range(0, site_config.num_color_key_cols):
        color_table.add_column(f"color_col_{i}", justify='center')

    while (row_number * site_config.num_color_key_cols) < num_colors:
        idx = row_number * site_config.num_color_key_cols
        color_table.add_row(*COLOR_KEYS[idx:(idx + site_config.num_color_key_cols)])
        row_number += 1

    print_centered(vertically_pad(color_table))


def print_other_page_link(epstein_files: 'EpsteinFiles') -> None:
    if args._site_type == SiteType.MOBILE:
        return
    elif args._site_type == SiteType.CURATED:
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


def print_section_header(msg: str, style: str = SECTION_HEADER_STYLE, is_centered: bool = False) -> None:
    if args._site_type == SiteType.CURATED:
        console.line(2)
        print_section_links()

    panel = Panel(Text(msg, justify='center'), expand=True, padding=(1, 1), style=style)
    panel = Align.center(panel) if is_centered else panel
    console.print(Padding(panel, (2, 25, 1, 25)))


def print_section_links(style: str = '') -> None:
    """Print links to the various sections within the curated page."""
    print_centered(build_demi_table(SECTION_LINK_MSG, SECTION_LINKS), style=style)


def print_section_summary_table(table: Table) -> None:
    """Precede it with internal section links if it's the curated page."""
    print_centered(Padding(table, (2, 0, 2, 0)))


def print_title_page_top() -> None:
    """Top half of the title page."""
    _print_page_title()

    # panel with links to all the sites
    links_txts = [_bulleted_site_link(site_type, link) for site_type, link in SiteType.all_links().items()]

    if args.mobile:
        num_link_indent_spaces = 0
    else:
        max_link_len = max(len(link.plain) for link in links_txts)
        num_link_indent_spaces = max(2, int((len(SITE_GLOSSARY_MSG) - max_link_len) / 2)) - 2

    sites_txt = Text('').append(SITE_GLOSSARY_MSG, style='wheat4 bold').append('\n\n')
    sites_txt.append(indent_txt(join_texts(links_txts, '\n'), num_link_indent_spaces))
    print_centered(Panel(sites_txt, border_style='dim', padding=(1, site_config.site_glossary_horizontal_padding)))
    console.line()

    # warning and internal links
    _print_starred_header(site_config.not_all_files_warning, num_spaces=0, num_stars=0)
    print_centered(f"This dataset includes everything from the {HOUSE_OVERSIGHT_TRANCHE}", style=DATASET_DESCRIPTION_STYLE)
    print_centered(f"as well as a curated selection of the {DOJ_2026_TRANCHE}.", style=DATASET_DESCRIPTION_STYLE)


def print_title_page_bottom(epstein_files: 'EpsteinFiles') -> None:
    """Bottom half of the title page."""
    console.line()
    _print_abbreviations_table()
    print_centered(epstein_files.overview_table())
    console.line()
    print_color_key()
    print_centered(f"(if you think there's an attribution error or can deanonymize an {UNKNOWN} contact {CRYPTADAMUS_TWITTER})", 'grey46')
    print_centered(f"(thanks to {link_markup('https://x.com/ImDrinknWyn', '@ImDrinknWyn', 'dodger_blue3')} + others for help attributing redacted emails)")
    _print_external_links()
    console.line()


def _bulleted_site_link(site_type: SiteType, link: Text) -> Text:
    # the mobile site is just a different rendering of the curated site
    if args.mobile:
        you_are_here = YOU_ARE_HERE if site_type == SiteType.MOBILE else ''
    else:
        you_are_here = YOU_ARE_HERE if site_type == args._site_type else ''

    return Text('➱ ').append(link).append(' ').append(you_are_here)


def _link_with_comment(url: str, comment: str | Text, _link_text: str = '') -> Text:
    link_text = _link_text if _link_text else (JMAIL if url == JMAIL_URL else '')

    if isinstance(comment, Text):
        comment = comment
        link_style = 'navajo_white3 bold'
    else:
        comment = enclose(Text(comment, 'color(195) dim italic'), '()', 'gray27')
        link_style = EXTERNAL_STYLE

    return link_text_obj(url, link_text=link_text, style=link_style).append(' ').append(comment)


def _print_abbreviations_table() -> None:
    table = build_table(title="Abbreviations Used Frequently In These Conversations", show_header=False)
    table.add_column("Abbreviation", justify="center", style='bold')

    table.add_column(
        "Translation",
        justify="center",
        min_width=site_config.abbreviations_width,
        style="white"
    )

    for k, v in HEADER_ABBREVIATIONS.items():
        table.add_row(highlighter(k), v)

    console.print(Align.center(vertically_pad(table)))


def _print_external_links() -> None:
    console.line()
    print_centered(Text('External Links', style=TABLE_TITLE_STYLE))
    doj_search_link = join_texts([link_text_obj(DOJ_SEARCH_URL, 'search', style=ARCHIVE_ALT_LINK_STYLE)], encloser='()')
    print_centered(_link_with_comment(DOJ_2026_URL, doj_search_link, 'DOJ Epstein Files Transparency Act Disclosures'))
    raw_docs_link = link_text_obj(OVERSIGHT_DRIVE_URL, 'raw files', style=ARCHIVE_ALT_LINK_STYLE)
    raw_docs_link = join_texts([raw_docs_link], encloser='()')
    print_centered(_link_with_comment(OVERSIGHT_REPUBS_PRESSER_URL, raw_docs_link, '2025 Oversight Committee Press Release'))

    for url, link in EXTERNAL_LINK_MSGS.items():
        print_centered(_link_with_comment(url, link))


def _print_page_title(width: int = TITLE_WIDTH) -> None:
    if not args.mobile:
        print_centered(MOBILE_WARNING, style='dim')

    title = Text('', justify='center').append('The Epstein Files', style='underline bold')
    title_panel = Panel(title, box=box.DOUBLE_EDGE, expand=True, padding=(2, 2), style=TITLE_STYLE, width=width)
    print_centered(vertically_pad(title_panel))

    print_centered_link(
        SUBSTACK_URL,
        "I Made Epstein's Text Messages Great Again (And You Should Read Them)",
        style=f'{SUBSTACK_POST_LINK_STYLE} bold'
    )

    if not args.mobile:
        print_centered_link(SUBSTACK_URL, SUBSTACK_URL.removeprefix('https://'), style=f'{SUBSTACK_POST_LINK_STYLE} dim')

    print_centered(join_texts(CRYPTADAMUS_SOCIAL_LINKS, join=site_config.social_link_separator))
    console.line()


def _print_starred_header(msg: str, num_stars: int = 7, num_spaces: int = 2, style: str = WARNING_STYLE) -> None:
    """String like '  *** Title Msg ***  '."""
    print_centered(wrap_in_markup_style(starred_header(msg, num_stars, num_spaces), style))
