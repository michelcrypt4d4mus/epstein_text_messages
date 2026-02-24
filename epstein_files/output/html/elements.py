from copy import copy, deepcopy
from os import devnull
from pathlib import Path
from typing import Literal, Mapping

from rich.console import Console
from rich.style import Style
from rich.text import Text

from epstein_files.output.rich import CONSOLE_KWARGS
from epstein_files.util.helpers.data_helpers import sort_dict_by_keys
from epstein_files.util.helpers.file_helper import log_file_write
from epstein_files.util.logging import logger

CssUnit = str | int
Side = Literal['top', 'left', 'right', 'bottom']
SideProp = Literal['margin', 'padding']

CODE_TEMPLATE = '{code}'
SPLITTER = '-# JUNK #-'
HORIZONTAL_SIDES: list[Side] = ['left', 'right']
VERTICAL_SIDES: list[Side] = ['top', 'bottom']
ALL_SIDES: list[Side] = VERTICAL_SIDES + HORIZONTAL_SIDES
HTML_CONSOLE_kWARGS = copy(CONSOLE_KWARGS)

HTML_CONSOLE_kWARGS.update({
    'file': open(devnull, "wt"),
    'record': True,
})

PRE_TAG_CSS = {
    'font-family': "Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace",
}

CODE_TAG_CSS = {
    'font-family': 'inherit',
}

html_console = Console(**HTML_CONSOLE_kWARGS)


def code_console_template() -> str:
    return styled_tag('code', CODE_TEMPLATE, CODE_TAG_CSS)


def div_tag(contents: str, css_props: dict[str, str] | None = None) -> str:
    return styled_tag('div', contents, css_props)


def horizontal_margin_props(units: CssUnit) -> dict[str, str]:
    return side_props('margin', HORIZONTAL_SIDES, units)


def horizontal_pad_props(units: CssUnit) -> dict[str, str]:
    return side_props('padding', HORIZONTAL_SIDES, units)


def margin_props(horizontal: CssUnit, vertical: CssUnit) -> dict[str, str]:
    return {**vertical_margin_props(horizontal), **vertical_margin_props(vertical)}


def padding_props(horizontal: CssUnit, vertical: CssUnit) -> dict[str, str]:
    return {**horizontal_pad_props(horizontal), **vertical_pad_props(vertical)}


def pre_console_template() -> str:
    return styled_tag('pre', CODE_TEMPLATE, PRE_TAG_CSS)


def pre_code_console_template() -> str:
    return styled_tag('pre', code_console_template(), PRE_TAG_CSS)


def side_props(prop: SideProp, sides: list[Side], units: CssUnit) -> dict[str, str]:
    return {f"{prop}-{side}": to_px(units) for side in sides}


def styled_tag(tag: str, contents: str, css_props: dict[str, str] | None = None) -> str:
    """Surround `contents` with <tag style="[CSS_STRING]">."""
    if css_props:
        style_str = f' style="{to_inline_css(css_props)}"'
    else:
        style_str = ''

    return f'<{tag}{style_str}>{contents}</{tag}>'


def to_inline_css(d: Mapping[str, str | int]) -> str:
    css_props = [f'{k}: {v}' for k, v in sort_dict_by_keys(d).items()]
    return '; '.join(css_props)


def to_em(chars: int) -> str:
    return f"{chars}em"


def to_px(pixels: CssUnit) -> str:
    return f"{pixels}px" if isinstance(pixels, int) else pixels


def vertical_margin_props(units: CssUnit) -> dict[str, str]:
    return side_props('margin', VERTICAL_SIDES, units)


def vertical_pad_props(units: CssUnit) -> dict[str, str]:
    return side_props('padding', VERTICAL_SIDES, units)
