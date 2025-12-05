import re
from collections import defaultdict
from dataclasses import dataclass, field

from inflection import singularize

from epstein_files.documents.document import SearchResult
from epstein_files.documents.email_header import EmailHeader
from epstein_files.util.constant.common_words import COMMON_WORDS, COMMON_WORDS_LIST, UNSINGULARIZABLE_WORDS
from epstein_files.util.data import ALL_NAMES, Timer, flatten, sort_dict
from epstein_files.util.env import args, logger, specified_names
from epstein_files.util.file_helper import WORD_COUNT_HTML_PATH
from epstein_files.util.rich import (console, highlighter, print_centered, print_page_title, print_panel,
     print_social_media_links, print_starred_header, write_html)

FIRST_AND_LAST_NAMES = flatten([n.split() for n in ALL_NAMES])
NON_SINGULARIZABLE = UNSINGULARIZABLE_WORDS + [n.lower() for n in FIRST_AND_LAST_NAMES if n.endswith('s')]
SKIP_WORDS_REGEX = re.compile(r"^(asmallworld@|enwiki|http|imagepng|nymagcomnymetro|addresswww|mailto|www)|jee[vy]acation|(gif|html?|jpe?g|utm)$")
BAD_CHARS_REGEX = re.compile(r"[-–=+()$€£©°«—^&%!#/_`,.;:'‘’\"„“”?\d\\]")
NO_SINGULARIZE_REGEX = re.compile(r".*io?us$")
MAX_WORD_LEN = 45

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

FLAGGED_WORDS = []


@dataclass
class WordCount:
    count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    singularized: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def count_word(self, word: str, document_line: SearchResult) -> None:
        word = EmailHeader.cleanup_str(word).lower().strip()
        raw_word = word

        if word not in BAD_CHARS_OK:
            word = BAD_CHARS_REGEX.sub('', word).strip()

        if self._is_invalid_word(word):
            return
        elif word in SINGULARIZATIONS:
            word = SINGULARIZATIONS[word]
        elif not (word in NON_SINGULARIZABLE or NO_SINGULARIZE_REGEX.match(word) or len(word) <= 2):
            word = singularize(word)
            self.singularized[raw_word] += 1

            # Log the raw_word if we've seen it more than once (but only once)
            if raw_word.endswith('s') and self.singularized[raw_word] == 2:
                logger.info(f"Singularized '{raw_word}' to '{word}'...")

        if not self._is_invalid_word(word):
            self.count[word] += 1

        if word in FLAGGED_WORDS:
            logger.warning(f"{document_line.document.filename}: Found '{word}' in '{document_line.lines[0]}'")

    def _is_invalid_word(self, w: str) -> bool:
        return bool(SKIP_WORDS_REGEX.search(w)) \
            or len(w) <= 1 \
            or len(w) >= MAX_WORD_LEN \
            or w in COMMON_WORDS \
            or w in BAD_WORDS
