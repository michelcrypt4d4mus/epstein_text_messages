import re
from collections import defaultdict
from copy import deepcopy

from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.text import Text

from epstein_files.output.highlight_config import HIGHLIGHT_GROUPS
from epstein_files.util.constant.strings import REGEX_STYLE_PREFIX
from epstein_files.util.env import args
from epstein_files.util.helpers.data_helpers import sort_dict
from epstein_files.util.logging import logger


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

            if args.debug and isinstance(re_highlight, re.Pattern):
                for match in re_highlight.finditer(text.plain):
                    type(self).highlight_counts[(match.group(1) or 'None').replace('\n', ' ')] += 1

    def print_highlight_counts(self, console: Console) -> None:
        """Print counts of how many times strings were highlighted."""
        highlight_counts = deepcopy(self.highlight_counts)
        weak_date_regex = re.compile(r"^(\d\d?/|20|http|On ).*")

        for highlighted, count in sort_dict(highlight_counts):
            if highlighted is None or weak_date_regex.match(highlighted):
                continue

            try:
                console.print(f"{highlighted:25s} highlighted {count} times")
            except Exception as e:
                logger.error(f"Failed to print highlight count {count} for {highlighted}")
