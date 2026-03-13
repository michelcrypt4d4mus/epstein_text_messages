"""
Small methods for building rich text constructs.
"""
import os

from rich.padding import Padding
from rich.text import Text

from epstein_files.util.constant.strings import QUESTION_MARKS
from epstein_files.util.helpers.string_helper import starred_header

left_indent_padding = lambda num_spaces: (0, 0, 0, num_spaces)
left_indent = lambda obj, num_spaces: Padding(obj, left_indent_padding(num_spaces))
no_bold = lambda style: style.replace('bold', '').strip()
suppress_output_console_kwargs = lambda: {'file': open(os.devnull, "wt")}
vertically_pad = lambda obj, amount = 1: Padding(obj, (amount, 0, amount, 0))

QUESTION_MARKS_TXT = Text(QUESTION_MARKS, style='grey50')
WARNING_STYLE = 'bold black on white'


def enclose(txt: str | Text, encloser: str = '', encloser_style: str = 'wheat4') -> Text:
    """Surround with something."""
    if not encloser:
        return Text('').append(txt)
    elif len(encloser) != 2:
        raise ValueError(f"'encloser' arg is '{encloser}' which is not 2 characters long")

    enclose_start, enclose_end = (encloser[0], encloser[1])
    return Text('').append(enclose_start, encloser_style).append(txt).append(enclose_end, encloser_style)


def join_non_empty(*txts, sep: str | Text = ' ') -> Text:
    """Join two strings but only if they are not empty."""
    sep = sep if isinstance(sep, Text) else Text(sep)
    return sep.join([t for t in txts if len(t) > 0])


def starred_header_txt(msg: str, num_stars: int = 7, num_spaces: int = 2, style: str = WARNING_STYLE) -> Text:
    """String like '  *** Title Msg ***  '."""
    return Text(starred_header(msg, num_stars, num_spaces), style)
