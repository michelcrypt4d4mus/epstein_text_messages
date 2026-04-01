# Rich reference: https://rich.readthedocs.io/en/latest/reference.html
import json
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
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

from epstein_files.documents.documents.categories import CategoryType, Interesting, Neutral, Uninteresting
from epstein_files.output.epstein_highlighter import highlighter
from epstein_files.output.highlight_config import HIGHLIGHT_GROUPS
from epstein_files.output.site.site_config import MobileConfig
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.data_helpers import json_safe, sort_dict
from epstein_files.util.helpers.rich_helpers import RAINBOW, left_indent_padding, suppress_output_console_kwargs
from epstein_files.util.helpers.string_helper import snip_msg
from epstein_files.util.logging import RICH_COLOR_SYSTEM, logger

GREY_NUMBERS = [58, 39, 39, 35, 30, 27, 23, 23, 19, 19, 15, 15, 15]
VALID_GREYS = [0, 3, 7, 11, 15, 19, 23, 27, 30, 35, 37, 39, 42, 46, 50, 53, 54, 58, 62, 63, 66, 69, 70, 74, 78, 82, 84, 85, 89, 93]
NA_TXT = Text(NA, style='dim')

DATASET_MSG_STYLE = 'gray74'
KEY_STYLE = 'dim'
KEY_STYLE_ALT = 'light_steel_blue3'
LAST_TIMESTAMP_STYLE = 'wheat4'
PATH_STYLE = 'deep_pink3'
STR_VAL_STYLE = 'cornsilk1 italic'
STR_VAL_STYLE_ALT = 'light_yellow3 italic'
SUBTITLE_STYLE = 'black on white'
SYMBOL_STYLE = 'grey70'
TABLE_BORDER_STYLE = 'grey46'
TABLE_TITLE_STYLE = f"gray54 italic"
TITLE_STYLE = 'black on white'  # color(103)'
TRIMMED_MSG_STYLE = 'dim italic'

CATEGORY_BG_STYLES: dict[CategoryType, str] = defaultdict(lambda: 'gray11')

CATEGORY_BG_STYLES.update({
    Interesting.MONEY: '#081a0d',
    Neutral.GOVERNMENT: '#060a2e',
    Neutral.LEGAL: 'rgb(25, 20, 25)',
})

DEFAULT_TABLE_KWARGS = {
    'border_style': TABLE_BORDER_STYLE,
    'caption_style': 'navajo_white3 dim italic',
    'header_style': "bold",
    'title_style': TABLE_TITLE_STYLE,
}

THEME_STYLES = {
    DEFAULT: 'wheat4',
    TEXT_LINK: 'deep_sky_blue4 underline',
    f"{REGEX_STYLE_PREFIX}.{HIGHLIGHTED_QUOTE}": 'white italic underline on gray15',
    f"{REGEX_STYLE_PREFIX}.reverse": 'reverse',
    **{hg.theme_style_name: hg.style for hg in HIGHLIGHT_GROUPS},
}

RICH_THEME = Theme(THEME_STYLES)


# Instantiate console object
CONSOLE_KWARGS = {
    'color_system': RICH_COLOR_SYSTEM,
    'highlighter': highlighter,
    'record': True, # args.build,
    'safe_box': True,
    'theme': RICH_THEME,
    'width': args.width,
}

if args.suppress_output:
    logger.warning(f"Suppressing terminal output because args.suppress_output={args.suppress_output}...")
    CONSOLE_KWARGS.update(suppress_output_console_kwargs())

console = Console(**CONSOLE_KWARGS)
mobile_console = Console(**{**CONSOLE_KWARGS, 'width': MobileConfig.width, **suppress_output_console_kwargs()})


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


def bool_txt(b: bool | None, match_width: bool = False) -> Text:
    """Colored True or False Text obj."""
    txt = Text('')

    if b is False:
        return txt.append(str(b), style='bright_red bold italic')
    elif b is True:
        return txt.append(f" {b}" if match_width else str(b), style='bright_green bold italic')
    else:
        return txt.append(str(b), style='dim italic')


def build_table(
    title: str | Text | None,
    cols: list[str | dict] | None = None,
    copy_props_from: Table | None = None,
    **kwargs
) -> Table:
    table = Table(title=title, **{**DEFAULT_TABLE_KWARGS, **kwargs})

    if copy_props_from:
        for k, v in vars(copy_props_from).items():
            if k.startswith('_') or k in ['columns', 'rows']:
                continue

            setattr(table, k, v)

    if cols:
        add_cols_to_table(table, cols)

    return table


def indent_txt(txt: str | Text, spaces: int = 4, prefix: str = '') -> Text:
    indent = Text(' ' * spaces).append(prefix)
    return indent + Text(f"\n{indent}").join(txt.split('\n'))


# TODO: unused
def left_indent(obj: RenderableType, num_spaces: int) -> Padding:
    """Add left padding to any `Renderable`."""
    return Padding(obj, left_indent_padding(num_spaces))


def prefix_with(
    txt: list[Text] | list[str] | Text | str,
    pfx: str,
    pfx_style: str = '',
    indent: str | int = ''
) -> Text:
    """Add a rich stylized prefix to a `Text`, `str`, or array of either."""
    indent = indent * ' ' if isinstance(indent, int) else indent

    lines = [
        Text('').append(f"{indent}{pfx} ", style=pfx_style).append(line)
        for line in (txt.split('\n') if isinstance(txt, (Text, str)) else txt)
    ]

    return Text('\n').join(lines)


def print_centered(obj: RenderableType, style: str = '') -> None:
    if args.mobile:
        if isinstance(obj, str):
            obj = Text.from_markup(obj, justify='center')
        elif isinstance(obj, Text):
            obj = Text('', justify='center').append(obj)

    console.print(Align.center(obj), highlight=False, style=style)


def print_json(obj: object, label: str = '', skip_falsey: bool = False) -> None:
    """Print an `object` as rich prettified / formatted JSON."""
    if isinstance(obj, dict):
        if skip_falsey:
            obj = {k: v for k, v in obj.items() if v}

        obj = json_safe(obj)

    console.line()

    if label:
        console.print(Panel(label, expand=False))

    console.print_json(json.dumps(obj, sort_keys=True), indent=4)
    console.line()


def print_special_note(note: str | Text) -> None:
    """Print an eye catching panel with extra info about a person."""
    print_centered(Padding(Panel(note, expand=True, padding=(1, 3), style='reverse'), (0, 0, 2, 0)))


def print_subtitle_panel(msg: str, style: str = SUBTITLE_STYLE) -> None:
    """A reverse color panel to put at the top of sections."""
    console.print(subtitle_panel(msg, style))


def quote_txt(t: Text | str, try_double_quote_first: bool = False, style: str = '') -> Text:
    """Wrap Text object in double or single quotes as appropriate."""
    if try_double_quote_first:
        quote_char = '"' if '"' not in t else "'"
    else:
        quote_char = "'" if "'" not in t else '"'

    return Text(quote_char, style=style).append(t).append(quote_char)


def snip_msg_txt(msg: str, style: str = '') -> Text:
    """Make it like <...msg...>. Uses markup in case there are links in `msg`"""
    txt = Text('', style=style)
    return txt.append(Text.from_markup(wrap_in_markup_style(snip_msg(msg), TRIMMED_MSG_STYLE)))


def section_subtitle_panel(msg: str, style: str = SUBTITLE_STYLE) -> Padding:
    """`subtitle_panel()` but with margins applied."""
    return Padding(subtitle_panel(msg, style), site_config.subtitle_margins)


def styled_dict(
    d: Mapping[str, bool | datetime | str | Path | Text | None],
    key_style: str = KEY_STYLE,
    sep: str = ': ',
    sort_fields: bool = True,
    min_indent: int = 20,
) -> Text:
    """Turn a dict into a colored representation."""
    key_lengths = [len(k) for k in d.keys()] + [min_indent]
    key_prefixes = list(set([k.split('.')[0] for k in d.keys() if '.' in k]))
    key_pfx_colors = {k: RAINBOW[i] for i, k in enumerate(key_prefixes)}

    key_colors = {
        k: key_pfx_colors.get(k.split('.')[0] if '.' in k else k, key_style)
        for k in d.keys()
    }

    return Text('\n').join([
        styled_key_value(k, v, key_style=key_colors.get(k, key_style), indent=max(key_lengths) + 3, sep=sep)
        for k, v in (sort_dict(d) if sort_fields else d.items())
    ])


def styled_key_value(
    key: str,
    val: bool | datetime | int | str | Path | Text | list | None,
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
        from epstein_files.people.entity import Entity

        if val and isinstance(val[0], Entity):
            val = [str(e) for e in val]

        val_txt = highlighter(json.dumps(val))
    elif isinstance(val, bool):
        val_txt = bool_txt(val)
    elif isinstance(val, datetime):
        val_txt = Text(str(val), style=TIMESTAMP_STYLE)
    elif isinstance(val, dict):
        val_txt = indent_txt(Text('\n').append(styled_dict(val)), 14)
    else:
        val_txt = None
        val_style = ''

        if isinstance(val, int):
            val = f"{val:,}"
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


def subtitle_panel(msg: str, style: str = SUBTITLE_STYLE) -> Panel:
    """`Panel`  for important text, like name of a subsection."""
    return Panel(
        Text.from_markup(msg, justify='center'),
        padding=site_config.subtitle_padding,
        style=style,
        width=site_config.subtitle_width,
    )


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


if args._debug_highlight_patterns:
    print_json(THEME_STYLES, 'THEME_STYLES')
