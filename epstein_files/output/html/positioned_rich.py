from dataclasses import dataclass, field
import os
from typing import Literal, Self

from rich.align import Align, AlignMethod
from rich.console import RenderableType
from rich.padding import Padding, PaddingDimensions
from rich.table import Table
from rich.text import Text

from epstein_files.util.helpers.data_helpers import add_lists
from epstein_files.util.logging import logger

CssUnit = int | str
CssProps = dict[str, str]
OptionalCssProps = CssProps | None
SideProp = Literal['margin', 'padding']

to_px = lambda pixels: f"{pixels}px" if isinstance(pixels, int) else pixels

# MAKEUP_PADDING to make HTML panel padding match ANSI (there's ~0.5 spaces between "a" and "|" in "a | b" in ansi)
MAKEUP_PADDING = 0.7
BORDER_HORIZONTAL_PADDING = 1
BORDER_VERTICAL_PADDING = MAKEUP_PADDING

# Side constants
Side = Literal['top', 'left', 'right', 'bottom']
HORIZONTAL_SIDES: list[Side] = ['left', 'right']
VERTICAL_SIDES: list[Side] = ['top', 'bottom']
ALL_SIDES: list[Side] = ['top', 'right', 'bottom', 'left']  # Order matters for converting PaddingDimension!

# dimensions are assumed to always be tuple[int, int, int, int] (but as a list)
horizontal_only = lambda dimensions: [0, dimensions[1], 0, dimensions[3]]
vertical_only = lambda  dimensions: [dimensions[0], 0, dimensions[2], 0]

# Margin CSS
dimensions_to_margin_css = lambda dimensions: _dimensions_to_layout_css('margin', dimensions)
margin_horizontal_css = lambda ems: dimensions_to_margin_css((0, ems))
margin_vertical_css = lambda ems: dimensions_to_margin_css((ems, 0))

# Padding CSS
dimensions_to_padding_css = lambda dimensions: _dimensions_to_layout_css('padding', dimensions)
padding_horizontal_css = lambda ems: dimensions_to_padding_css((0, ems))
padding_vertical_css = lambda ems: dimensions_to_padding_css((ems, 0))

# CSS constants
LEFT_JUSTIFIED = {'margin-right': 'auto'}
RIGHT_JUSTIFIED = {'margin-left': 'auto'}
CENTERED = {**LEFT_JUSTIFIED, **RIGHT_JUSTIFIED}
VERTICAL_MARGIN = 1.9

# CSS classes
BLACK_BACKGROUND = 'black_background'
NO_EXPAND = 'no_expand'
BLACK_BG__NO_EXPAND = f"{BLACK_BACKGROUND} {NO_EXPAND}"
PANEL_BODY_CSS_CLASS = f'{NO_EXPAND} document_body_container'


@dataclass
class PositionedRich:
    obj: RenderableType
    align: AlignMethod | None = None
    margin: list[int | float] = field(default_factory=lambda: [0] * 4)
    padding: list[int | float] = field(default_factory=lambda: [0] * 4)  # TODO: currently unused

    @classmethod
    def from_unwrapped_obj(cls, obj: RenderableType, positioned: Self | None = None) -> Self:
        """Alternate constructor to unwrap `Align` and `Padding` and collect the align/padding props in a PositionedRenderable."""
        positioned = positioned or cls(obj)

        if isinstance(obj, Align):
            positioned.align = obj.align
            return cls.from_unwrapped_obj(obj.renderable, positioned)
        elif isinstance(obj, Padding):
            positioned.margin = add_lists(positioned.margin, [obj.top, obj.right, obj.bottom, obj.left])
            return cls.from_unwrapped_obj(obj.renderable, positioned)
        else:
            positioned.obj = obj  # End recursion and set self.obj if obj is not an Align or Padding
            return positioned

    @property
    def alignment_css(self) -> CssProps:
        """margin-auto"""
        return alignment_css(self.align) if self.align else {}

    @property
    def css(self) -> CssProps:
        """Margin and alignment."""
        return {**self.alignment_css, **self.margin_css}

    @property
    def margin_css(self) -> CssProps:
        return dimensions_to_margin_css(self.margin)

    @property
    def margin_horizontal(self) -> list[int | float]:
        return horizontal_only(self.margin)

    @property
    def margin_horizontal_css(self) -> CssProps:
        return dimensions_to_margin_css(self.margin_horizontal)

    @property
    def margins_vertical(self) -> list[int | float]:
        return vertical_only(self.margin)

    @property
    def margins_vertical_css(self) -> CssProps:
        return dimensions_to_margin_css(self.margins_vertical)

    @property
    def margin_top(self) -> int | float:
        return self.margin[0]
    @property
    def margin_right(self) -> int | float:
        return self.margin[1]
    @property
    def margin_bottom(self) -> int | float:
        return self.margin[2]
    @property
    def margin_left(self) -> int | float:
        return self.margin[3]

    @property
    def requires_container_div(self) -> bool | None:
        """
        if both horizontal margin and alignment are set on the same side we need to place the div in a container
        with horizontal padding so the aligned element doesn't go all the way to edge of screen.
        """
        for margin_prop in self.margin_css.keys():
            if self.alignment_css.get(margin_prop):
                logger.info(f"{margin_prop} is set by both self.align='{self.align}' and self.margin={self.margin}, margin value wins out!")
                return True

    def to_html(self) -> str:
        from epstein_files.output.html.builder import table_to_html
        from epstein_files.output.html.elements import div_class, div_tag

        if not isinstance(self.obj, Table):
            raise NotImplementedError(f"Only Table objects can have to_html() called on them")

        # If we need both horizontal margin and horizontal alignment at same time we need two divs:
        if self.requires_container_div:
            #    [INNER DIV] uses only HORIZONTAL ALIGNMENT + vertical MARGIN
            inner_css = {**self.alignment_css, **self.margins_vertical_css}
            inner_div = table_to_html(self.obj, inner_css)

            #    [OUTER DIV] uses only HORIZONTAL MARGIN (as paddinging) with no vertical margin or padding
            outer_css = CENTERED if self.align == 'center' else self.margin_horizontal_css
            logger.warning(f"Built table with inner_css:\n{inner_css}\n\nouter_css:{outer_css}")
            return div_class(inner_div, BLACK_BG__NO_EXPAND, outer_css)
        else:
            # logger.warning(f"Table does not require inner + outer container to handle conflicting props: {self.css}")
            # TODO: seems liek the BLACK_BG__NO_EXPAND class should be applied somehow?
            logger.warning(f"Built table with self.css:\n{self.css}")
            return table_to_html(self.obj, self.css)

        return outer_div

    @classmethod
    def zero_dimensions(cls) -> list[int | float]:
        return [0, 0, 0, 0]


# TODO: should this also set text-align?
def alignment_css(align: AlignMethod) -> CssProps:
    """CSS margin-auto props to align things left, right, or center."""
    if align == 'center':
        return dict(CENTERED)
    elif align == 'left':
        return dict(LEFT_JUSTIFIED)
    elif align == 'right':
        return dict(RIGHT_JUSTIFIED)
    elif not align:
        return {}
    else:
        raise ValueError(f"unknown alignment value: '{align}'")


# CSS units
def to_em(num_chars: int | float) -> str:
    """Convert int to CSS em units (1em = size of character in the current font). 1 => "1em"."""
    if isinstance(num_chars, str) and num_chars.endswith('em'):
        logger.error(f"Trying to append a second 'em' to '{num_chars}'")
        return num_chars
    elif num_chars:
        return f"{num_chars}em"
    else:
        return ''


def unpack_dimensions(dimensions: PaddingDimensions) -> list[int]:
    """Unpack an int or 2-tuple to a 4-tuple (top, right, bottom, left)."""
    return list(Padding.unpack(dimensions))


def vertical_spacer(em_units: int | float) -> str:
    return f'<div style="height: {to_em(em_units)}"></div>'


def _dimensions_to_layout_css(prop: SideProp, dimensions: PaddingDimensions) -> CssProps:
    """Turn all non-zero side dimensions into appropriate margin- or padding- CSS props."""
    return {
        f"{prop}-{ALL_SIDES[i]}": to_em(value)
        for i, value in enumerate(unpack_dimensions(dimensions))
        if value
    }
