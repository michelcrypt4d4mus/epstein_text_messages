from rich.highlighter import RegexHighlighter

from .constants import *


class EpsteinTextHighlighter(RegexHighlighter):
    """Currently only highlights the email header."""
    base_style = f"{EMAIL_HEADER_FIELD}."

    highlights = [
        r"(?P<email>[\w-]+@([\w-]+\.)+[\w-]+)",  # TODO: doesn't work
        r"(?P<header>Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):",
    ]
