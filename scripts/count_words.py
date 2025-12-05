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
from epstein_files.util.data import ALL_NAMES, Timer, flatten, sort_dict
from epstein_files.util.env import args, logger, specified_emailers
from epstein_files.util.file_helper import WORD_COUNT_HTML_PATH
from epstein_files.util.rich import (console, highlighter, print_centered, print_page_title, print_panel,
     print_social_media_links, print_starred_header, write_html)

FIRST_AND_LAST_NAMES = flatten([n.split() for n in ALL_NAMES])
NON_SINGULARIZABLE = UNSINGULARIZABLE_WORDS + [n.lower() for n in FIRST_AND_LAST_NAMES if n.endswith('s')]
SKIP_WORDS_REGEX = re.compile(r"^(asmallworld@|enwiki|http|imagepng|nymagcomnymetro|addresswww|mailto|www)|jee[vy]acation|(gif|html?|jpe?g|utm)$")
BAD_CHARS_REGEX = re.compile(r"[-–=+()$€£©°«—^&%!#/_`,.;:'‘’\"„“”?\d\\]")
NO_SINGULARIZE_REGEX = re.compile(r".*io?us$")
PADDING = (0, 0, 2, 2)
MAX_WORD_LEN = 45
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

BAD_WORDS = [
    'classdhoenzbfont',
    'classdmsonormaluucauup',
    'contenttransferencoding',
    'fortunehtmlsmidnytnowsharesmprodnytnow',
    'inthe',
    'summarypricesquotesstatistic',
]

BAD_CHARS_OK = [
    "he'll",
    'MLPF&S'.lower(),
    'reis-dennis',
]

# inflection.singularize() messes these up
SINGULARIZATIONS = {
    'abuses': 'abuse',
    'approves': 'approve',
    'arrives': 'arrive',
    'awards/awards': 'award',
    'bann': 'bannon',
    'believes': 'believe',
    'busses': 'bus',
    'colletcions': 'collection',
    'dies': 'die',
    'dives': 'dive',
    'drives': 'drive',
    'enterpris': 'enterprise',
    'girsl': 'girl',
    'gives': 'give',
    'involves': 'involve',
    'jackies': 'jackie',
    'leaves': 'leave',
    'lies': 'lie',
    'lives': 'live',
    'loves': 'love',
    'missives': 'missive',
    'police': 'police',
    'proves': 'prove',
    'receives': 'receive',
    'reserves': 'reserve',
    'shes': 'she',
    'slaves': 'slave',
    'thnks': 'thank',
    'thieves': 'thief',
    'toes': 'toe',
    'viruses': 'virus',
    'woes': 'woe',
    #'trying': 'try',
}


def is_invalid_word(w: str) -> bool:
    return bool(SKIP_WORDS_REGEX.search(w)) or len(w) <= 1 or len(w) >= MAX_WORD_LEN or w in COMMON_WORDS


timer = Timer()
print_page_title(expand=False)
print_social_media_links()
console.line(2)
epstein_files = EpsteinFiles.get_files()
print_starred_header(f"Most Common Words in the {len(epstein_files.emails):,} Emails")
print_centered(f"(excluding {len(COMMON_WORDS_LIST)} particularly common words at bottom)", style='dim')
console.line()
words = defaultdict(int)
singularized = defaultdict(int)

for email in sorted(epstein_files.emails, key=lambda e: e.file_id):
    if email.is_duplicate or email.is_junk_mail:
        logger.info(f"Skipping duplicate or junk file '{email.filename}'...")
        continue
    elif specified_emailers:
        if email.author not in specified_emailers:
            logger.debug(f"Skipping email from '{email.author}'...")
            continue
        elif email.file_id in EMAIL_IDS_TO_SKIP:
            logger.debug(f"Skipping EMAIL_IDS_TO_SKIP '{email.file_id}' from '{email.author}'...")
            continue

    for line in email.actual_text.split('\n'):
        if line.startswith('htt'):
            continue

        for word in line.split():
            word = EmailHeader.cleanup_str(word).lower().strip()
            raw_word = word

            if word not in BAD_CHARS_OK:
                word = BAD_CHARS_REGEX.sub('', word).strip()

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

            if word in FLAGGED_WORDS:
                logger.warning(f"{email.filename}: Found '{word}' in '{line}'")

txts_to_print = [
    highlighter(Text('').append(f"{word}", style='wheat4').append(': ').append(f"{count:,}"))
    for word, count in [kv for kv in sort_dict(words) if kv[1] >= MIN_COUNT_CUTOFF]
    if word not in BAD_WORDS
]

cols = Columns(txts_to_print, column_first=False, equal=False, expand=True)
console.print(Padding(cols, PADDING))
console.print(f"Showing {len(txts_to_print):,} words appearing at least {MIN_COUNT_CUTOFF} times (out of {len(words):,} words).")
console.line(3)
print_panel(f"{len(COMMON_WORDS_LIST):,} Excluded Words")
console.print(', '.join(COMMON_WORDS_LIST), highlight=False)
write_html(WORD_COUNT_HTML_PATH)
timer.print_at_checkpoint(f"Finished counting words")
