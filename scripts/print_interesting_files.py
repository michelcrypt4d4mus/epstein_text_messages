#!/usr/bin/env python
# Print list of all files with non-null is_interesting value along with counts of interestingness.
from collections import defaultdict

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.util.helpers.debugging_helper import print_interesting_doc_panels_and_props
from epstein_files.util.logging import logger
from epstein_files.output.rich import bool_txt, console, styled_dict, print_subtitle_panel


counts: dict[str, int] = defaultdict(int)

for doc in epstein_files.all_documents:
    counts[str(doc.is_interesting)] += 1

    if doc.is_interesting is not None:
        txt = bool_txt(doc.is_interesting, match_width=True).append(': ').append(doc.summary)

        if doc.config_description_txt:
            txt.append(' ').append(doc.config_description_txt)

        console.print(txt)


console.print(f"\nInterestingness counts:")
console.print(styled_dict(counts))
console.line
