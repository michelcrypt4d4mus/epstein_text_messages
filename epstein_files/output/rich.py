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
from epstein_files.output.highlight_config import HIGHLIGHT_GROUPS, HIGHLIGHTED_NAMES
from epstein_files.util.constant.strings import *
from epstein_files.util.constant.urls import *
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import json_safe, sort_dict
from epstein_files.util.helpers.link_helper import link_markup
from epstein_files.util.logging import logger

SUBTITLE_WIDTH = 110
NA_TXT = Text(NA, style='dim')
SKIPPED_FILE_MSG_PADDING = (0, 0, 0, 4)
SUBTITLE_PADDING = (2, 0, 1, 0)
GREY_NUMBERS = [58, 39, 39, 35, 30, 27, 23, 23, 19, 19, 15, 15, 15]
VALID_GREYS = [0, 3, 7, 11, 15, 19, 23, 27, 30, 35, 37, 39, 42, 46, 50, 53, 54, 58, 62, 63, 66, 69, 70, 74, 78, 82, 84, 85, 89, 93]

DATASET_DESCRIPTION_STYLE = 'gray74'
INFO_STYLE = 'white dim italic'
KEY_STYLE = 'dim'
KEY_STYLE_ALT = 'light_steel_blue3'
LAST_TIMESTAMP_STYLE = 'wheat4'
PATH_STYLE = 'deep_pink3'
STR_VAL_STYLE = 'cornsilk1 italic'
STR_VAL_STYLE_ALT = 'light_yellow3 italic'
SYMBOL_STYLE = 'grey70'
TABLE_BORDER_STYLE = 'grey46'
TABLE_TITLE_STYLE = f"gray54 italic"
TITLE_STYLE = 'black on white'  # color(103)'
WARNING_STYLE = 'bold black on white'

DEFAULT_TABLE_KWARGS = {
    'border_style': TABLE_BORDER_STYLE,
    'caption_style': 'navajo_white3 dim italic',
    'header_style': "bold",
    'title_style': TABLE_TITLE_STYLE,
}

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


def enclose(txt: str | Text, encloser: str = '', encloser_style: str = 'wheat4') -> Text:
    """Surround with something."""
    if not encloser:
        return Text('').append(txt)
    elif len(encloser) != 2:
        raise ValueError(f"'encloser' arg is '{encloser}' which is not 2 characters long")

    enclose_start, enclose_end = (encloser[0], encloser[1])
    return Text('').append(enclose_start, encloser_style).append(txt).append(enclose_end, encloser_style)


def indent_txt(txt: str | Text, spaces: int = 4, prefix: str = '') -> Text:
    indent = Text(' ' * spaces).append(prefix)
    return indent + Text(f"\n{indent}").join(txt.split('\n'))


def join_texts(txts: Sequence[str | Text], join: str = ' ', encloser: str = '', encloser_style: str = 'wheat4') -> Text:
    """Join rich.Text objs into one."""
    txt = Text('')

    for i, _txt in enumerate(txts):
        txt.append(join if i >= 1 else '').append(enclose(_txt, encloser, encloser_style))

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


def print_json(label: str, obj: object, skip_falsey: bool = False) -> None:
    if isinstance(obj, dict):
        if skip_falsey:
            obj = {k: v for k, v in obj.items() if v}

        obj = json_safe(obj)

    console.line()
    console.print(Panel(label, expand=False))
    console.print_json(json.dumps(obj, sort_keys=True), indent=4)
    console.line()


def print_starred_header(msg: str, num_stars: int = 7, num_spaces: int = 2, style: str = WARNING_STYLE) -> None:
    """String like '  *** Title Msg ***  '."""
    stars = '*' * num_stars
    spaces = ' ' * num_spaces
    msg = f"{spaces}{stars} {msg} {stars}{spaces}"
    print_centered(wrap_in_markup_style(msg, style))


def print_subtitle_panel(msg: str, style: str = 'black on white') -> None:
    panel = Panel(Text.from_markup(msg, justify='center'), width=SUBTITLE_WIDTH, style=style)
    print_centered(Padding(panel, SUBTITLE_PADDING))


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


if args.colors_only:
    print_json('THEME_STYLES', THEME_STYLES)
