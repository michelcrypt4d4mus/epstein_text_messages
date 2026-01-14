#!/usr/bin/env python
# Print arguments used to correct emails to a dict
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.documents.document import Document
from epstein_files.util.data import all_elements_same


print("LINE_REPAIR_MERGES = {")

for email in Document.sort_by_id(epstein_files.emails):
    if not email._line_merge_arguments:
        continue

    args = [list(arg) for arg in email._line_merge_arguments]
    key_str = f"    '{email.file_id}':"

    if len(args) > 1 and all_elements_same(args):
        print(f"{key_str} [{args[0]}] * {len(args)},")
    else:
        print(f"{key_str} {args},")

print("}")
