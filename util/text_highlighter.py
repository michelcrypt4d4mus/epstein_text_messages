from rich.highlighter import RegexHighlighter

from .constants import *


class EpsteinTextHighlighter(RegexHighlighter):
    """Apply style to anything that looks like an email."""
    base_style = f"{HEADER_FIELD}."

    highlights = [
        r"(?P<email>[\w-]+@([\w-]+\.)+[\w-]+)",
        r"(?P<header>Date|From|Sent|To|C[cC]|Importance|Subject|Bee|B[cC]{2}|Attachments):",
    ]
