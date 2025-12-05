#!/usr/bin/env python
# Count word usage in emails (and texts?)
import re
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()
from inflection import singularize
from rich.columns import Columns
from rich.padding import Padding
from rich.text import Text

from epstein_files.documents.document import SearchResult
from epstein_files.documents.email_header import EmailHeader
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.constant.common_words import COMMON_WORDS, COMMON_WORDS_LIST
from epstein_files.util.data import ALL_NAMES, Timer, flatten, sort_dict
from epstein_files.util.env import args, logger, specified_names
from epstein_files.util.file_helper import WORD_COUNT_HTML_PATH
from epstein_files.util.rich import (console, highlighter, print_centered, print_page_title, print_panel,
     print_social_media_links, print_starred_header, write_html)
from epstein_files.util.word_count import WordCount

PADDING = (0, 0, 2, 2)
MIN_COUNT_CUTOFF = 3
FLAGGED_WORDS = []

EMAIL_IDS_TO_SKIP = [
    '029692',  # WaPo article
    '029779',  # WaPo article
    '026298',  # Written by someone else?
    '026755',  # HuffPo
    '023627',  # Wolff article about epstein
    '031569',  # Article by Kathryn Alexeeff
    '030528',  # Vicky Ward article
    '030522',  # Vicky Ward article
]


timer = Timer()
print_page_title(expand=False)
print_social_media_links()
console.line(2)
epstein_files = EpsteinFiles.get_files()
print_starred_header(f"Most Common Words in the {len(epstein_files.emails):,} Emails")
print_centered(f"(excluding {len(COMMON_WORDS_LIST)} particularly common words at bottom)", style='dim')
console.line()
word_count = WordCount()

for email in sorted(epstein_files.emails, key=lambda e: e.file_id):
    if email.is_duplicate or email.is_junk_mail:
        logger.info(f"Skipping duplicate or junk file '{email.filename}'...")
        continue
    elif specified_names:
        if email.author not in specified_names:
            logger.debug(f"Skipping email from '{email.author}'...")
            continue
        elif email.file_id in EMAIL_IDS_TO_SKIP:
            logger.debug(f"Skipping EMAIL_IDS_TO_SKIP '{email.file_id}' from '{email.author}'...")
            continue

    for line in email.actual_text.split('\n'):
        if line.startswith('htt'):
            continue

        for word in line.split():
            word_count.count_word(word, SearchResult(email, [line]))

word_txts = [
    highlighter(Text('').append(f"{word}", style='wheat4').append(': ').append(f"{count:,}"))
    for word, count in [kv for kv in sort_dict(word_count.count) if kv[1] >= MIN_COUNT_CUTOFF]
]

cols = Columns(word_txts, column_first=False, equal=False, expand=True)
console.print(Padding(cols, PADDING))
console.print(f"Showing {len(word_txts):,} words appearing at least {MIN_COUNT_CUTOFF} times (out of {len(word_count.count):,} words).")
console.line(3)
print_panel(f"{len(COMMON_WORDS_LIST):,} Excluded Words")
console.print(', '.join(COMMON_WORDS_LIST), highlight=False)
write_html(WORD_COUNT_HTML_PATH)
timer.print_at_checkpoint(f"Finished counting words")
