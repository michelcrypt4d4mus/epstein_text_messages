from rich.table import Table
from rich.text import Text

from epstein_files.util.rich import highlighter

HEADER_INDENT = Text('        ')
VERTICAL_BAR = '┃ '  # ⎹┃┇┋❘⦀🁢⏐┃⎹
TOP_BAR = '🁢 '


class LeftBarPanel(Table):
    """Create a faux `Panel` that just has a single vertical line down the left side."""
    @classmethod
    def build(cls, text: str | Text, bar_style: str, header: str | Text = ''):
        table = cls.grid(padding=0)
        table.add_column(justify='left', style=bar_style)  # Column for the line
        table.add_column(justify='left')                   # Column for content

        if header:
            table.add_row(TOP_BAR, header)
            table.add_row(VERTICAL_BAR, '')

        for txt_line in highlighter(text).split('\n'):
            table.add_row(VERTICAL_BAR, txt_line)

        return table
