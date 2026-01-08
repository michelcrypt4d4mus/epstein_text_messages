import re
from collections import defaultdict
from dataclasses import dataclass, field

from inflection import singularize
from rich.columns import Columns
from rich.console import Console, ConsoleOptions, RenderResult
from rich.padding import Padding
from rich.text import Text

from epstein_files.documents.emails.email_header import EmailHeader
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.constant.common_words import COMMON_WORDS_LIST, COMMON_WORDS, UNSINGULARIZABLE_WORDS
from epstein_files.util.constant.names import OTHER_NAMES
from epstein_files.util.constant.output_files import WORD_COUNT_HTML_PATH
from epstein_files.util.data import ALL_NAMES, flatten, sort_dict
from epstein_files.util.env import args
from epstein_files.util.logging import logger
from epstein_files.util.rich import (console, highlighter, print_centered, print_color_key, print_page_title,
     print_panel, print_starred_header, write_html)
from epstein_files.util.search_result import MatchedLine, SearchResult
from epstein_files.util.timer import Timer

FIRST_AND_LAST_NAMES = flatten([n.split() for n in ALL_NAMES])
FIRST_AND_LAST_NAMES = [n.lower() for n in FIRST_AND_LAST_NAMES] + OTHER_NAMES

HTML_REGEX = re.compile(r"^http|#yiv|com/|cae-v2w=|content-(transfe|type)|font(/|-(family|size))|http|\.html?\??|margin-bottom|padding-left|quoted-printable|region=|text-decoration|ttps|www|\.(gif|jpe?g|png);?$")
HYPHENATED_WORD_REGEX = re.compile(r"[a-z]+-[a-z]+", re.IGNORECASE)
OK_SYMBOL_WORDS = ['mar-a-lago', 'p/e', 's&p', ':)', ':).', ';)', ':-)', ';-)']
ONLY_SYMBOLS_REGEX = re.compile(r"^[^a-zA-Z0-9]+$")
SYMBOL_WORD_REGEX = re.compile(r"^[-—–@%/?.,&=]+$")
SPLIT_WORDS_BY = ['@', '/']
FLAGGED_WORDS = []  # For debugging, log extra info when one of these is encountered

NON_SINGULARIZABLE = UNSINGULARIZABLE_WORDS + [n for n in FIRST_AND_LAST_NAMES if n.endswith('s')]
SKIP_WORDS_REGEX = re.compile(r"^(asmallworld@|enwiki|http|imagepng|nymagcomnymetro|addresswww|mailto|www|/font|colordu|classdms|targetdblank|nymagcom|palmbeachdailynews)|jee[vy]acation|fontfamily|(gif|html?|jpe?g|utm)$")
BAD_CHARS_REGEX = re.compile(r"[-–=+()$€£©°«—^&%!#_`,.;:'‘’\"„“”?\d\\]")
NO_SINGULARIZE_REGEX = re.compile(r".*[io]us$")
PADDING = (0, 0, 2, 2)
MIN_COUNT_CUTOFF = 3
MAX_WORD_LEN = 45

BAD_WORDS = [
    'charsetutf',
    'classdhoenzbfont',
    'classdmsonormaluucauup',
    'contenttransferencoding',
    'dbfcefacdbfla',
    'ehomep',
    'facedarial',
    'fortunehtmlsmidnytnowsharesmprodnytnow',
    'inthe',
    'quotedprintable',
    'researchdisclosureinquiries@jpmorgancom',
    'summarypricesquotesstatistic',
    'emichotpmiamiheraldcom',
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
    'deserves': 'deserve',
    'dies': 'die',
    'dives': 'dive',
    'drives': 'drive',
    'enterpris': 'enterprise',
    'focuses': 'focus',
    'foes': 'foe',
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
    'selfies': 'selfie',
    'serves': 'serve',
    'shes': 'she',
    'sholes': 'scholes',
    'slaves': 'slave',
    'thnks': 'thank',
    'ties': 'tie',
    'thieves': 'thief',
    'toes': 'toe',
    #'trying': 'try',
    'viruses': 'virus',
    'waves': 'wave',
    'woes': 'woe',
    # spelling
    'prostituion': 'prostitution',
    'visoki': 'visoski',
    # eh...
    'twittercom': 'twitter',
}


@dataclass
class WordCount:
    count: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    singularized: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def tally_word(self, word: str, document_line: SearchResult) -> None:
        word = EmailHeader.cleanup_str(word).lower().strip()
        raw_word = word

        if HTML_REGEX.search(word):
            logger.info(f" Skipping HTML word '{word}'")
            return
        elif SYMBOL_WORD_REGEX.match(word):
            logger.debug(f" Skipping symbol word '{word}'")
            return
        elif word in OK_SYMBOL_WORDS:
            self.count[':)' if word == ':).' else word] += 1
            return
        elif HYPHENATED_WORD_REGEX.search(word):
            logger.info(f"  Word with hyphen: '{word}'")

        if ONLY_SYMBOLS_REGEX.match(word):
            logger.info(f"    ONLY_SYMBOLS_REGEX match: '{word}'")
            return

        if word not in BAD_CHARS_OK:
            word = BAD_CHARS_REGEX.sub('', word).strip()

        if self._is_invalid_word(word):
            return
        elif SYMBOL_WORD_REGEX.match(word):
            logger.debug(f" Skipping symbol word '{word}'")
            return

        for symbol in SPLIT_WORDS_BY:
            if symbol not in word:
                continue

            for w in word.split(symbol):
                self.tally_word(w, document_line)

            logger.info(f"  Split word with '{symbol}' in it '{word}'...")
            return

        if word in SINGULARIZATIONS:
            word = SINGULARIZATIONS[word]
        elif not (word in NON_SINGULARIZABLE or NO_SINGULARIZE_REGEX.match(word) or len(word) <= 2):
            word = singularize(word)
            self.singularized[raw_word] += 1

            # Log the raw_word if we've seen it more than once (but only once)
            if raw_word.endswith('s') and self.singularized[raw_word] == 2:
                logger.info(f"    Singularized '{raw_word}' to '{word}'...")

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

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        word_txts = [
            highlighter(Text('').append(f"{word}", style=_word_style(word)).append(': ').append(f"{count:,}"))
            for word, count in [kv for kv in sort_dict(self.count) if kv[1] >= MIN_COUNT_CUTOFF]
        ]

        cols = Columns(word_txts, column_first=False, equal=False, expand=True)
        yield Padding(cols, PADDING)
        yield f"Showing {len(word_txts):,} words appearing at least {MIN_COUNT_CUTOFF} times (out of {len(self.count):,} words)."


def write_word_counts_html() -> None:
    timer = Timer()
    epstein_files = EpsteinFiles.get_files(timer)
    email_subjects: set[str] = set()
    word_count = WordCount()
    # Remove dupes, junk mail, and fwded articles from emails
    emails = [e for e in epstein_files.non_duplicate_emails() if not (e.is_junk_mail() or e.is_fwded_article())]

    for email in emails:
        if args.names and email.author not in args.names:
            continue

        logger.info(f"Counting words in {email}\n  [SUBJECT] {email.subject()}")
        lines = email.actual_text.split('\n')

        if email.subject() not in email_subjects and f'Re: {email.subject()}' not in email_subjects:
            email_subjects.add(email.subject())
            lines.append(email.subject())

        for i, line in enumerate(lines):
            if HTML_REGEX.search(line):
                continue

            for word in line.split():
                word_count.tally_word(word, SearchResult(email, [MatchedLine(line, i)]))

    # Add in iMessage conversations
    for imessage_log in epstein_files.imessage_logs:
        logger.info(f"Counting words in {imessage_log}")

        for i, msg in enumerate(imessage_log.messages):
            if args.names and msg.author not in args.names:
                continue
            elif HTML_REGEX.search(msg.text):
                continue

            for word in msg.text.split():
                word_count.tally_word(word, SearchResult(imessage_log, [MatchedLine(msg.text, i)]))

    print_page_title(expand=False)
    print_starred_header(f"Most Common Words in {len(emails):,} Emails and {len(epstein_files.imessage_logs)} iMessage Logs")
    print_centered(f"(excluding {len(COMMON_WORDS_LIST)} particularly common words at bottom)", style='dim')
    console.line()
    print_color_key()
    console.line()
    console.print(word_count)
    console.line(2)
    print_panel(f"{len(COMMON_WORDS_LIST):,} Excluded Words", centered=True)
    console.print(', '.join(COMMON_WORDS_LIST), highlight=False)
    write_html(WORD_COUNT_HTML_PATH)
    timer.print_at_checkpoint(f"Finished counting words")


def _word_style(word: str | None) -> str:
    word = word or ''
    return 'bright_white' if word in FIRST_AND_LAST_NAMES else 'grey53'
