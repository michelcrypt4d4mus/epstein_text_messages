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

from epstein_files.documents.email_header import EmailHeader
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.constant.common_words import COMMON_WORDS, COMMON_WORDS_LIST, UNSINGULARIZABLE_WORDS
from epstein_files.util.data import ALL_NAMES, flatten, sort_dict
from epstein_files.util.env import args, logger
from epstein_files.util.file_helper import WORD_COUNT_HTML_PATH
from epstein_files.util.rich import console, highlighter, print_centered, print_page_title, print_panel, write_html

FIRST_AND_LAST_NAMES = flatten([n.split() for n in ALL_NAMES])
NON_SINGULARIZABLE = UNSINGULARIZABLE_WORDS + [n.lower() for n in FIRST_AND_LAST_NAMES if n.endswith('s')]
SKIP_WORDS_REGEX = re.compile(r"^(http|addresswww|mailto|www)|jee[vy]acation|(gif|html?|jpe?g|utm)$")
BAD_CHARS_REGEX = re.compile(r"[-–=+()$€£©°«—^&%!#/_`,.;:'‘’\"„“”?\d\\]")
NO_SINGULARIZE_REGEX = re.compile(r".*io?us$")
FLAGGED_WORDS = []
MAX_WORD_LEN = 45
MIN_COUNT_CUTOFF = 2

BAD_CHARS_OK = [
    'MLPF&S'.lower(),
    'reis-dennis',
]

# inflection.singularize() messes these up
SINGULARIZATIONS = {
    'approves': 'approve',
    'arrives': 'arrive',
    'awards/awards': 'award',
    'believes': 'believe',
    'busses': 'bus',
    'colletcions': 'collection',
    'dives': 'dive',
    'drives': 'drive',
    'enterpris': 'enterprise',
    'gives': 'give',
    'involves': 'involve',
    'jackies': 'jackie',
    'leaves': 'leave',
    'lies': 'lie',
    'lives': 'live',
    'loves': 'love',
    'missives': 'missive',
    'proves': 'prove',
    'receives': 'receive',
    'reserves': 'reserve',
    'shes': 'she',
    'slaves': 'slave',
    'thnks': 'thank',
    'thieves': 'thief',
    'toes': 'toe',
    #'trying': 'try',
}


def is_invalid_word(w: str) -> bool:
    return bool(SKIP_WORDS_REGEX.search(w)) or len(w) <= 1 or len(w) >= MAX_WORD_LEN or w in COMMON_WORDS


print_page_title(expand=False)
epstein_files = EpsteinFiles()
print_centered(f"Most Common Words in the {len(epstein_files.emails):,} Emails\n")
words = defaultdict(int)
singularized = defaultdict(int)

for email in sorted(epstein_files.emails, key=lambda e: e.file_id):
    if email.is_duplicate:
        logger.info(f"Skipping duplicate file '{email.filename}'...")
        continue

    for line in email.actual_text(use_clean_text=True, skip_header=True).split('\n'):
        if line.startswith('htt'):
            continue

        for word in line.split():
            word = EmailHeader.cleanup_str(word).lower().strip()
            raw_word = word

            if word not in BAD_CHARS_OK:
                word = BAD_CHARS_REGEX.sub('', word).strip()

            if word in FLAGGED_WORDS:
                logger.warning(f"Found '{word}' in '{line}'")

            if is_invalid_word(word):
                continue
            elif word in SINGULARIZATIONS:
                word = SINGULARIZATIONS[word]
            elif not (word in NON_SINGULARIZABLE or NO_SINGULARIZE_REGEX.match(word) or len(word) <= 2):
                word = singularize(word)
                singularized[raw_word] += 1

                # Log the raw_word if we've seen it more than once (but only once)
                if raw_word.endswith('s') and singularized[raw_word] == 2:
                    logger.info(f"Singularized '{raw_word}' to '{word}'...")

            if not is_invalid_word(word):
                words[word] += 1

words_to_print = [kv for kv in sort_dict(words) if kv[1] > MIN_COUNT_CUTOFF]

txts_to_print = [
    Text('').append(f"{word:>{MAX_WORD_LEN}}", style='wheat4').append(': ').append(f"{count:,}")
    for word, count in words_to_print
]

for txt_line in txts_to_print:
    console.print(txt_line)

console.line(3)
console.print(f"Showing {len(words_to_print):,} words appearing at least {MIN_COUNT_CUTOFF} time (out of {len(words):,} words).\n")
print_panel(f"{len(COMMON_WORDS_LIST):,} Excluded Words")
console.print(', '.join(COMMON_WORDS_LIST), highlight=False)
write_html(WORD_COUNT_HTML_PATH)

txts_to_print = [
    highlighter(Text('').append(f"{word}", style='wheat4').append(': ').append(f"{count:,}"))
    for word, count in words_to_print
]

console.line(4)
cols = Columns(txts_to_print[0:400], column_first=True, equal=False, expand=False)
console.print(Padding(cols, (0, 0, 0, 2)))
console.line(4)
