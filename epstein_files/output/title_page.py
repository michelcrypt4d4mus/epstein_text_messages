"""
Methods that print the title page with all the links etc.
"""
# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
from rich import box
from rich.align import Align
from rich.console import Console, Group, NewLine, RenderableType
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from epstein_files.output.epstein_highlighter import highlighter
from epstein_files.output.layout_elements.demi_table import build_demi_table
from epstein_files.output.highlight_config import HIGHLIGHTED_NAMES
from epstein_files.output.rich import *
from epstein_files.output.site.internal_links import SECTION_ANCHORS
from epstein_files.output.site.site_config import MOBILE_WARNING_TXT
from epstein_files.people.names import UNKNOWN
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.constants import HEADER_ABBREVIATIONS, TEXT_MSG_ABBREVIATIONS
from epstein_files.util.env import args, site_config
from epstein_files.util.external_link import SUBSTACK_POST_LINK_STYLE, join_texts, link_markup, link_text_obj, parenthesize
from epstein_files.util.helpers.rich_helpers import starred_header_txt, vertically_pad
from epstein_files.util.helpers.string_helper import starred_header
from epstein_files.util.logging import logger

SECTION_LINK_MSG = 'jump to a different section of this page'
SUBTITLE_WIDTH = 110
TITLE_WIDTH = 50

DATASET_MSG_STYLE = 'gray74'
OTHER_PAGE_MSG_STYLE = 'gray78 dim'
STR_VAL_STYLE = 'cornsilk1 italic'
STR_VAL_STYLE_ALT = 'light_yellow3 italic'
SECTION_HEADER_STYLE = 'bold black on color(146)'

DATASET_MSG_LINES = [
    f"This dataset includes everything from the {HOUSE_OVERSIGHT_TRANCHE}",
    f"as well as a curated selection of the {DOJ_2026_TRANCHE}",
    f"with a particular focus on cryptocurrency",
    f"and women who speak Russian.",
]

DATASET_MSG_TXTS = [Text(msg, justify='center', style=DATASET_MSG_STYLE) for msg in DATASET_MSG_LINES]
DATASET_MSG = Align.center(join_texts(DATASET_MSG_TXTS, '\n'))

# label of the HighlightedNames objects colors with the style of that same HighlightedNames
COLOR_KEYS = [
    Text(highlight_group.label.replace('_', ' '), style=highlight_group.style)
    for highlight_group in sorted(HIGHLIGHTED_NAMES, key=lambda hg: hg.label)
]

SECTION_LINKS = [
    link_text_obj(internal_link_url(anchor), section_name, 'indian_red')
    for section_name, anchor in SECTION_ANCHORS.items()
]


def color_key() -> Padding:
    color_table = build_table('Rough Guide to Highlighted Colors', show_header=False)
    num_colors = len(COLOR_KEYS)
    row_number = 0

    for i in range(0, site_config.num_color_key_cols):
        color_table.add_column(f"color_col_{i}", justify='center')

    while (row_number * site_config.num_color_key_cols) < num_colors:
        idx = row_number * site_config.num_color_key_cols
        color_table.add_row(*COLOR_KEYS[idx:(idx + site_config.num_color_key_cols)])
        row_number += 1

    return vertically_pad(color_table)


def header_elements() -> list[RenderableType]:
    title = Text('', justify='center').append('The Epstein Files', style='underline bold')
    title_panel = Panel(title, box=box.DOUBLE_EDGE, expand=True, padding=(2, 2), style=TITLE_STYLE, width=TITLE_WIDTH)
    title_with_vertical_margin = vertically_pad(title_panel)

    # unwrapped, css_props = unwrap_rich(title_with_vertical_margin)
    # print(f"rich obj {unwrapped} has unwrapped title_panel css: {css_props}")
    # import pdb;pdb.set_trace()

    elements = [
        MOBILE_WARNING_TXT,
        title_with_vertical_margin,
        SUBSTACK_POST_TXT_MSGS_LINK,
    ]

    if not args.mobile:
        substack_link = SUBSTACK_POST_TXT_MSGS_LINK.url_link
        substack_link.stylize(f'{SUBSTACK_POST_LINK_STYLE} dim')
        elements.append(substack_link)

    elements.append(join_texts(CRYPTADAMUS_SOCIAL_LINKS, join=site_config.social_link_separator))
    return elements


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
    if args._site == Site.CURATED_MOBILE:
        return
    elif args._site == Site.CURATED:
        txt = THE_OTHER_PAGE_TXT + Text(f' is uncurated and has all {len(epstein_files.emails):,} emails')
        txt.append(f" and {len(epstein_files.other_files):,} unclassifiable files")
    else:
        txt = THE_OTHER_PAGE_TXT + (f' displays a curated collection of emails and')
        txt.append(" unclassifiable files of particular interest")

    print_centered(parenthesize(txt), style=OTHER_PAGE_MSG_STYLE)
    chrono_emails_link = link_text_obj(Site.get_url(Site.EMAILS_CHRONOLOGICAL), 'a page', style='light_slate_grey bold')
    chrono_emails_txt = Text(f"there's also ").append(chrono_emails_link)
    chrono_emails_txt.append(' with all the emails in chronological order')
    print_centered(parenthesize(chrono_emails_txt), style=OTHER_PAGE_MSG_STYLE)


# TODO: move to .rich
def section_header(msg: str, style: str = SECTION_HEADER_STYLE, is_centered: bool = False) -> Padding:
    """Make a padded Panel that's centered."""
    panel = Panel(Text(msg, justify='center'), expand=True, padding=(1, 1), style=style)
    panel = Align.center(panel) if is_centered else panel
    return Padding(panel, site_config.section_header_padding)


def title_page_bottom_elements(epstein_files: 'EpsteinFiles') -> list[RenderableType]:
    return [
        NewLine(),
        _abbreviations_table(),
        Text('External Links', style=TABLE_TITLE_STYLE),
        *[link for link in sorted(EXTERNAL_LINKS, key=lambda link: -len(link.__rich__()))],
        NewLine(),
        epstein_files.overview_table(),
        color_key(),
        Text.from_markup(f"(if you think there's an attribution error or can deanonymize an {UNKNOWN} contact {CRYPTADAMUS_X_LINK_MARKUP})", style='grey46'),
        Text.from_markup(f"(thanks to {link_markup('https://x.com/ImDrinknWyn', '@ImDrinknWyn', 'dodger_blue3')} + others for help attributing redacted emails)"),
        NewLine(),
    ]


def _abbreviations_table() -> Padding:
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

    if args.output_texts:
        for k, v in TEXT_MSG_ABBREVIATIONS.items():
            table.add_row(highlighter(k), v)

    return vertically_pad(table)
