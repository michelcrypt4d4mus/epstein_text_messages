import logging
import re
from collections import defaultdict
from copy import deepcopy

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.highlighter import RegexHighlighter, ReprHighlighter
from rich.text import Text

from epstein_files.output.highlight_config import HIGHLIGHT_GROUPS, HIGHLIGHTED_NAMES
from epstein_files.util.constant.strings import JEE, REGEX_STYLE_PREFIX
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import sort_dict

from epstein_files.util.logging import DOC_TYPE_STYLES, logger

WEAK_DATE_REGEX = re.compile(r"^(\d\d?/|20|http|On ).*")


class EpsteinHighlighter(RegexHighlighter):
    """Finds and colors interesting keywords based on the above config."""
    base_style = f"{REGEX_STYLE_PREFIX}."
    highlights: list[re.Pattern] = [highlight_group.regex for highlight_group in HIGHLIGHT_GROUPS]
    highlight_counts = defaultdict(int)

    def highlight(self, text: Text) -> None:
        """overrides https://rich.readthedocs.io/en/latest/_modules/rich/highlighter.html#RegexHighlighter"""
        highlight_regex = text.highlight_regex

        for re_highlight in self.highlights:
            highlight_regex(re_highlight, style_prefix=self.base_style)

            if args.stats and isinstance(re_highlight, re.Pattern):
                # if re_highlight.search(text.plain):
                #     logger.debug(f"Matched pattern {re_highlight.pattern}")

                for match in re_highlight.finditer(text.plain):
                    matched_str = (match.group(1) or 'None').replace('\n', ' ').strip().lower()
                    # logger.debug(f"Matched string {match.group(1)}")
                    type(self).highlight_counts[matched_str] += 1

    def print_highlight_counts(self, console: Console) -> None:
        """Print counts of how many times strings were highlighted."""
        console.print(Panel('Highlight counts', expand=False))
        highlight_counts = deepcopy(self.highlight_counts)

        for highlighted, count in sort_dict(highlight_counts):
            if highlighted is None or WEAK_DATE_REGEX.match(highlighted):
                continue

            try:
                console.print(f"{highlighted:25s} highlighted {count} times")
            except Exception as e:
                logger.error(f"Failed to print highlight count {count} for {highlighted}")


class NonEpsteinHighlighter(EpsteinHighlighter):
    """Doesn't highlight Epstein's name, highlights only `HighlightedNames` patterns (no `HighlightPatterns`)."""
    highlights: list[re.Pattern] = [hn.regex for hn in HIGHLIGHTED_NAMES if hn.label not in [JEE]]


def temp_highlighter(pattern: str, theme_style: str) -> EpsteinHighlighter:
    """
    Temporary highlighter that adds `pattern` to the usual highlight regexes.

    Args:
        theme_style (str): must be defined in THEME_STYLES with regex prefix.
    """
    class TempHighlighter(EpsteinHighlighter):
        highlights = [
            re.compile(fr"(?P<{theme_style}>{pattern})", re.IGNORECASE),
            *EpsteinHighlighter.highlights,
        ]

    return TempHighlighter()


highlighter = EpsteinHighlighter()
non_epstein_highlighter = NonEpsteinHighlighter()
