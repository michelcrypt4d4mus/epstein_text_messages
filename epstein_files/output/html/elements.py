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

from epstein_files.output.html.positioned_rich import PositionedRich, unpack_dimensions, CssProps, OptionalCssProps
from epstein_files.output.rich import CONSOLE_KWARGS, RICH_THEME
from epstein_files.util.constant.html import FONT_FAMILY, HTML_TERMINAL_THEME
from epstein_files.util.helpers.data_helpers import listify, sort_dict_by_keys
from epstein_files.util.helpers.string_helper import quote
from epstein_files.util.logging import logger

# Types
HtmlListTag = Literal['ol', 'ul']
HtmlElements = str | list[str]

# HTML templating vars
CODE_TEMPLATE = '{code}'
SPLITTER = '-# JUNK #-'
SPLITTER_TEMPLATE = SPLITTER + """{stylesheet} {background} {foreground}"""  # these template vars allow export_html() to work
# rich.Console for converting rich renderables to HTML
HTML_CONSOLE_KWARGS = copy(CONSOLE_KWARGS)
HTML_CONSOLE_KWARGS.update({'file': open(devnull, "wt"), 'record': True})

# CSS dicts
CODE_TAG_CSS = {'font-family': 'inherit'}
FONT_CSS_PROPS = {'font-family': FONT_FAMILY}
WIDTH_PROPS = ['max-width', 'width']

# Used by the per object rich -> html renders, e.g print_renderable, panel_to_div, etc.
HTML_RENDER_CONSOLE = Console(**HTML_CONSOLE_KWARGS)


def build_html_list(elements: list[str], list_type: HtmlListTag = 'ul', **kwargs) -> str:
    txt_htmls = [tag('li', t) for t in elements]

    if not elements:
        logger.warning(f"No elements to make <{list_type}> for...")
        return ''

    return tag(list_type, '\n'.join(txt_htmls), **kwargs)


def div_tag(contents: HtmlElements, css_props: OptionalCssProps = None, **kwargs) -> str:
    return tag('div', contents, css_props, **kwargs)


def div_class(contents: HtmlElements, class_name: str, css_props: OptionalCssProps = None, **kwargs) -> str:
    return div_tag(contents, css_props, class_name=class_name, **kwargs)


def div_with_legend(contents: HtmlElements, legend: str, css_props: OptionalCssProps = None, **kwargs) -> str:
    """Use <fieldset> + <legend>: https://css-tricks.com/how-to-add-text-in-borders-using-basic-html-elements/"""
    css_props = css_props or {}

    if legend:
        legend_css_props = {'color': css_props.get('border-color', 'white')}
        contents = tag('legend', legend, legend_css_props) + contents

    return tag('fieldset', contents, css_props, **kwargs)


def from_em(units: str | None) -> int | None:
    if not units:
        return None

    return int(units.removesuffix('em'))


def strip_outer_tag(_html: str, tag: str) -> str:
    html = re.sub(fr"^\s*<{tag}.*?>", '', _html)
    html = re.sub(fr"</{tag}>\s*$", '', html)

    if html == _html:
        logger.warning(f"asked to strip <{tag}> from {html} but nothing stripped...")

    return html


def tag(tag: str, contents: HtmlElements, css_props: OptionalCssProps = None, **kwargs) -> str:
    """Surround `contents` with <tag style="[CSS_STRING]">."""
    tag_kwargs = f' style="{to_inline_css(css_props)}"' if css_props else ''

    if kwargs:
        if 'class_name' in kwargs:
            kwargs['class'] = kwargs.pop('class_name')

        tag_kwargs += ' ' + ' '.join([f'{k}={quote(v)}' for k, v in kwargs.items()])

    return f"<{tag}{tag_kwargs}>{_html_elements_to_str(contents)}</{tag}>"


def to_inline_css(d: Mapping[str, str | int]) -> str:
    return '; '.join([f'{k}: {v}' for k, v in sort_dict_by_keys(d).items() if v])


def _html_elements_to_str(contents: HtmlElements) -> str:
    """no impact on the actual HTML rendering, newlines just for debugging."""
    return '\n'.join(listify(contents))


# "PRE" because it makes <pre> tags
PRE_CONSOLE_TEMPLATE_PREFIX = tag('pre', CODE_TEMPLATE, {})
PRE_CONSOLE_TEMPLATE = PRE_CONSOLE_TEMPLATE_PREFIX + SPLITTER_TEMPLATE
