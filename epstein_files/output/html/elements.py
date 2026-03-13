import re
from copy import copy
from dataclasses import dataclass, field
from os import devnull
from pathlib import Path
from typing import Literal, Mapping

from rich.align import AlignMethod
from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.padding import PaddingDimensions
from rich.style import Style
from rich.text import Text

from epstein_files.output.rich import CONSOLE_KWARGS, RICH_THEME
from epstein_files.util.constant.html import FONT_FAMILY, HTML_TERMINAL_THEME
from epstein_files.util.helpers.data_helpers import listify, sort_dict_by_keys
from epstein_files.util.helpers.string_helper import quote
from epstein_files.util.logging import logger

# Typps
CssProps = dict[str, str]
CssPropsArg = CssProps | None
CssUnit = str | int

HtmlListTag = Literal['ol', 'ul']
Side = Literal['top', 'left', 'right', 'bottom']
SideProp = Literal['margin', 'padding']

HORIZONTAL_SIDES: list[Side] = ['left', 'right']
VERTICAL_SIDES: list[Side] = ['top', 'bottom']
ALL_SIDES: list[Side] = ['top', 'right', 'bottom', 'left']  # Order matters for converting PaddingDimension!

CODE_TEMPLATE = '{code}'
SPLITTER = '-# JUNK #-'
SPLITTER_TEMPLATE = SPLITTER + """{stylesheet} {background} {foreground}"""  # these template vars allow export_html() to work

# CSS classes
BLACK_BACKGROUND = 'black_background'
BLACK_BG__NO_EXPAND = f"{BLACK_BACKGROUND} no_expand"

# CSS dicts
CENTERED = {'margin-left': 'auto', 'margin-right': 'auto'}
CODE_TAG_CSS = {'font-family': 'inherit'}
FONT_CSS_PROPS = {'font-family': FONT_FAMILY}
HTML_CONSOLE_KWARGS = copy(CONSOLE_KWARGS)
HTML_CONSOLE_KWARGS.update({'file': open(devnull, "wt"), 'record': True})
PRE_TAG_CSS = {}
WIDTH_PROPS = ['max-width', 'width']

DEFAULT_HTML_CONSOLE = Console(**HTML_CONSOLE_KWARGS)


def alignment_css(align: AlignMethod) -> CssProps:
    """left, right, center."""
    if align == 'center':
        return copy(CENTERED)
    elif align == 'left':
        return {'margin-right': 'auto'}
    elif align == 'right':
        return {'margin-left': 'auto'}
    else:
        raise ValueError(f"unknown alignment value: '{align}'")


def div_tag(contents: str, css_props: CssPropsArg = None, **kwargs) -> str:
    return tag('div', contents, css_props, **kwargs)


def div_class(contents: str, class_name: str, css_props: CssPropsArg = None, **kwargs) -> str:
    return div_tag(contents, css_props, class_name=class_name, **kwargs)


def div_with_legend(contents: str, legend: str, css_props: CssPropsArg = None, **kwargs) -> str:
    """Use <fieldset> + <legend>: https://css-tricks.com/how-to-add-text-in-borders-using-basic-html-elements/"""
    css_props = css_props or {}

    if legend:
        legend_css_props = {'color': css_props.get('border-color', 'white')}
        contents = tag('legend', legend, legend_css_props) + contents

    return tag('fieldset', contents, css_props)


def from_em(units: str | None) -> int | None:
    if not units:
        return None

    return int(units.removesuffix('em'))


def horizontal_margin_props(units: CssUnit) -> dict[str, str]:
    return side_props('margin', HORIZONTAL_SIDES, units)


def horizontal_pad_props(units: CssUnit) -> dict[str, str]:
    return side_props('padding', HORIZONTAL_SIDES, units)


def list_tag(elements: list[str], list_tag: HtmlListTag = 'ul', **kwargs) -> str:
    if not elements:
        logger.warning(f"No elements to make <{list_tag}> for...")
        return ''

    txt_htmls = [tag('li', t) for t in elements]
    return tag(list_tag, '\n'.join(txt_htmls), **kwargs)


def margin_props(horizontal: CssUnit, vertical: CssUnit) -> dict[str, str]:
    return {**vertical_margin_props(horizontal), **vertical_margin_props(vertical)}


def margin_tuple_to_props(dimensions: PaddingDimensions):
    return sides_tuple_to_props('margin', dimensions)


def padding_props(horizontal: CssUnit, vertical: CssUnit) -> dict[str, str]:
    return {**horizontal_pad_props(horizontal), **vertical_pad_props(vertical)}


def padding_tuple_to_props(dimensions: PaddingDimensions, constant: int | float = 0):
    """`constant` args adds a consant value to all 4 sides of padding."""
    padding_with_constant = tuple(d + constant for d in unpack_padding(dimensions))
    return sides_tuple_to_props('padding', padding_with_constant)


def side_props(prop: SideProp, sides: list[Side], units: CssUnit) -> dict[str, str]:
    return {f"{prop}-{side}": to_px(units) for side in sides}


def sides_tuple_to_props(side_prop: Literal['margin', 'padding'], dimensions: PaddingDimensions) -> CssProps:
    return {
        f"{side_prop}-{ALL_SIDES[i]}": to_em(amount)
        for i, amount in enumerate(unpack_padding(dimensions))
        if amount
    }


def strip_outer_tag(_html: str, tag: str) -> str:
    html = re.sub(fr"^\s*<{tag}.*?>", '', _html)
    html = re.sub(fr"</{tag}>\s*$", '', html)

    if html == _html:
        logger.warning(f"asked to strip <{tag}> from {html} but nothing stripped...")

    return html


def tag(tag: str, contents: str, css_props: CssPropsArg = None, **kwargs) -> str:
    """Surround `contents` with <tag style="[CSS_STRING]">."""
    tag_kwargs = f' style="{to_inline_css(css_props)}"' if css_props else ''

    if kwargs:
        if 'class_name' in kwargs:
            kwargs['class'] = kwargs.pop('class_name')

        tag_kwargs += ' ' + ' '.join([f'{k}={quote(v)}' for k, v in kwargs.items()])

    return f'<{tag}{tag_kwargs}>{contents}</{tag}>'


def to_inline_css(d: Mapping[str, str | int]) -> str:
    css_props = [f'{k}: {v}' for k, v in sort_dict_by_keys(d).items() if v]
    return '; '.join(css_props)


def to_em(chars: int | float | None) -> str:
    return f"{chars}em" if chars else ''


def to_px(pixels: CssUnit) -> str:
    return f"{pixels}px" if isinstance(pixels, int) else pixels


def unpack_padding(_dimensions: PaddingDimensions) -> tuple[int | float, int | float, int | float, int | float]:
    if isinstance(_dimensions, int):
        dimensions = [_dimensions]
    else:
        dimensions = list(_dimensions)

    if len(dimensions) == 1:
        dimensions = dimensions * 4
    elif len(dimensions) == 2:
        dimensions = dimensions * 2
    elif len(dimensions) != 4:
        raise ValueError(f"unknown padding dimension: {_dimensions}")

    return tuple(dimensions)


def vertical_margin_props(units: CssUnit) -> dict[str, str]:
    return side_props('margin', VERTICAL_SIDES, units)


def vertical_pad_props(units: CssUnit) -> dict[str, str]:
    return side_props('padding', VERTICAL_SIDES, units)


def vertical_spacer(em_units: int) -> str:
    return f'<div style="height: {em_units}"></div>'


PRE_CONSOLE_TEMPLATE_PREFIX = tag('pre', CODE_TEMPLATE, PRE_TAG_CSS)
PRE_CONSOLE_TEMPLATE = PRE_CONSOLE_TEMPLATE_PREFIX + SPLITTER_TEMPLATE
