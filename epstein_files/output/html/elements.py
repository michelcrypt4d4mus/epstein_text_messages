import re
from copy import copy
from dataclasses import dataclass, field
from os import devnull
from pathlib import Path
from typing import Literal, Mapping

from rich.console import Console, RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from epstein_files.output.rich import CONSOLE_KWARGS
from epstein_files.util.constant.html import FONT_FAMILY, HTML_TERMINAL_THEME
from epstein_files.util.helpers.data_helpers import sort_dict_by_keys
from epstein_files.util.helpers.string_helper import quote
from epstein_files.util.logging import logger

CssProps = dict[str, str] | None
CssUnit = str | int
Side = Literal['top', 'left', 'right', 'bottom']
SideProp = Literal['margin', 'padding']

HORIZONTAL_SIDES: list[Side] = ['left', 'right']
VERTICAL_SIDES: list[Side] = ['top', 'bottom']
ALL_SIDES: list[Side] = VERTICAL_SIDES + HORIZONTAL_SIDES

CODE_TEMPLATE = '{code}'
SPLITTER = '-# JUNK #-'
SPLITTER_TEMPLATE = SPLITTER + """{stylesheet} {background} {foreground}"""  # these template vars allow export_html() to work

# CSS classes
BLACK_BG = 'black_background'

# CSS dicts
CODE_TAG_CSS = {'font-family': 'inherit'}
FONT_CSS_PROPS = {'font-family': FONT_FAMILY}
HTML_CONSOLE_KWARGS = copy(CONSOLE_KWARGS)
HTML_CONSOLE_KWARGS.update({'file': open(devnull, "wt"), 'record': True})
PRE_TAG_CSS = {}

html_console = Console(**HTML_CONSOLE_KWARGS)


@dataclass
class HtmlStyle:
    _style: Style | str | None
    style: Style = field(init=False)

    def __post_init__(self):
        self.style = self._style if isinstance(self._style, Style) else Style.parse(self._style or '')

    @property
    def bg_hex(self) -> str:
        if self.style.bgcolor:
            return self.style.bgcolor.get_truecolor(HTML_TERMINAL_THEME).hex
        else:
            return ''

    @property
    def hex(self) -> str:
        if self.style.color:
            return self.style.color.get_truecolor(HTML_TERMINAL_THEME).hex
        else:
            return ''

    @property
    def to_css(self) -> dict[str, str]:
        props = {}

        if self.bg_hex:
            props['background-color'] = self.bg_hex
        if self.hex:
            props['color'] = self.hex

        return props


def div_tag(contents: str, css_props: CssProps = None, **kwargs) -> str:
    return tag('div', contents, css_props, **kwargs)


def div_class(contents: str, class_name: str, css_props: CssProps = None, **kwargs) -> str:
    return div_tag(contents, css_props, class_name=class_name, **kwargs)


def from_em(units: str | None) -> int | None:
    if not units:
        return None

    return int(units.removesuffix('em'))


def horizontal_margin_props(units: CssUnit) -> dict[str, str]:
    return side_props('margin', HORIZONTAL_SIDES, units)


def horizontal_pad_props(units: CssUnit) -> dict[str, str]:
    return side_props('padding', HORIZONTAL_SIDES, units)


def list_tag(elements: list[str], list_tag: Literal['ol', 'ul'] = 'ul', **kwargs) -> str:
    if not elements:
        logger.warning(f"No elements to make <{list_tag}> for...")
        return ''

    txt_htmls = [tag('li', t) for t in elements]
    return tag(list_tag, '\n'.join(txt_htmls), **kwargs)


def margin_props(horizontal: CssUnit, vertical: CssUnit) -> dict[str, str]:
    return {**vertical_margin_props(horizontal), **vertical_margin_props(vertical)}


def padding_props(horizontal: CssUnit, vertical: CssUnit) -> dict[str, str]:
    return {**horizontal_pad_props(horizontal), **vertical_pad_props(vertical)}


def side_props(prop: SideProp, sides: list[Side], units: CssUnit) -> dict[str, str]:
    return {f"{prop}-{side}": to_px(units) for side in sides}


def strip_outer_tag(_html: str, tag: str) -> str:
    html = re.sub(fr"^\s*<{tag}.*?>", '', _html)
    html = re.sub(fr"</{tag}>\s*$", '', html)

    if html == _html:
        logger.warning(f"asked to strip <{tag}> from {html} but nothing stripped...")

    return html


def tag(tag: str, contents: str, css_props: CssProps = None, **kwargs) -> str:
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


def vertical_margin_props(units: CssUnit) -> dict[str, str]:
    return side_props('margin', VERTICAL_SIDES, units)


def vertical_pad_props(units: CssUnit) -> dict[str, str]:
    return side_props('padding', VERTICAL_SIDES, units)


PRE_CONSOLE_TEMPLATE_PREFIX = tag('pre', CODE_TEMPLATE, PRE_TAG_CSS)
PRE_CONSOLE_TEMPLATE = PRE_CONSOLE_TEMPLATE_PREFIX + SPLITTER_TEMPLATE
