from rich.align import Align
from rich import box
from rich.table import Table
from rich.text import Text
from typing import Sequence


def build_demi_table(left_col_msg: str, right_col_list: Sequence[str | Text]) -> list[Align]:
    container = Table(box=box.ROUNDED, show_header=False, collapse_padding=True, show_edge=False, style='gray23')
    container.add_column('msg', width=19, style='dim', justify='right')
    container.add_column('link', justify='left')
    inner_list = Table(show_header=False, collapse_padding=True, show_edge=False, style='gray23')
    inner_list.add_column('link', justify='left')

    for element in right_col_list:
        inner_list.add_row(element)

    container.add_row(left_col_msg, inner_list)
    top_bottom_border = Text('-' * 50, style='grey15')

    pieces = [
        top_bottom_border,
        container,
        top_bottom_border
    ]

    return [Align.center(p) for p in pieces]
