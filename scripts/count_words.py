#!/usr/bin/env python
# Count word usage in emails (and texts?)
import re
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()
from rich.text import Text

from epstein_files.documents.email_header import EmailHeader
from epstein_files.util.constant.common_words import COMMON_WORDS
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.env import args
from epstein_files.util.rich import console, print_json

BAD_CHARS_REGEX = re.compile(r"[-=()$&%!#/_`,.;:'’\"”?\\\d]")
SKIP_WORDS_REGEX = re.compile(r"^(http|addresswww)|jeevacation|html$")


epstein_files = EpsteinFiles()
words = defaultdict(int)

for email in sorted(epstein_files.emails, key=lambda e: e.file_id):
    if email.is_duplicate:
        continue

    for word in email.actual_text(True).split():
        word = BAD_CHARS_REGEX.sub('', EmailHeader.cleanup_str(word).lower()).strip()

        if word and (50 > len(word) > 1) and word not in COMMON_WORDS and not SKIP_WORDS_REGEX.search(word):
            words[word] += 1

sort_key = lambda item: item[0] if args.sort_alphabetical else [item[1], item[0]]

for word, count in sorted(words.items(), key=sort_key, reverse=True):
    console.print(Text('').append(f"{word:>45}", style='wheat4').append(': ').append(f"{count:,}"))
