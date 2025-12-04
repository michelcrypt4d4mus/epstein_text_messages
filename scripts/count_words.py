#!/usr/bin/env python
# Count word usage in emails (and texts?)
import re
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()
from rich.text import Text

from epstein_files.documents.email_header import EmailHeader
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.constant.common_words import COMMON_WORDS, COMMON_WORDS_LIST
from epstein_files.util.env import args, logger
from epstein_files.util.file_helper import WORD_COUNT_HTML_PATH
from epstein_files.util.rich import console, print_centered, print_page_title, print_panel, write_html

BAD_CHARS_REGEX = re.compile(r"[-=+()$^&%!#/_`,.;:'’\"”?\d\\]")
SKIP_WORDS_REGEX = re.compile(r"^(http|addresswww)|jee[vy]acation|html?$")
MAX_WORD_LEN = 45


print_page_title(expand=False)
epstein_files = EpsteinFiles()
print_centered(f"Most Common Words in the {len(epstein_files.emails):,} Emails\n")
words = defaultdict(int)

for email in sorted(epstein_files.emails, key=lambda e: e.file_id):
    if email.is_duplicate:
        logger.info(f"Skipping duplicate file '{email.filename}'...")
        continue

    for word in email.actual_text(True).split():
        word = BAD_CHARS_REGEX.sub('', EmailHeader.cleanup_str(word).lower()).strip()

        if word and (MAX_WORD_LEN > len(word) > 1) and word not in COMMON_WORDS and not SKIP_WORDS_REGEX.search(word):
            words[word] += 1

sort_key = lambda item: item[0] if args.sort_alphabetical else [item[1], item[0]]

for word, count in sorted(words.items(), key=sort_key, reverse=True):
    console.print(Text('').append(f"{word:>{MAX_WORD_LEN}}", style='wheat4').append(': ').append(f"{count:,}"))

console.line(3)
console.print(f"Printed {len(words):,} words.\n")
print_panel(f"{len(COMMON_WORDS_LIST):,} Excluded Words")
console.print(', '.join(COMMON_WORDS_LIST), highlight=False)
write_html(WORD_COUNT_HTML_PATH)
