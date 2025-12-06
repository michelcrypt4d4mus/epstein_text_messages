#!/usr/bin/env python
# Count word usage in emails (and texts?)
from dotenv import load_dotenv
load_dotenv()

from epstein_files.documents.document import SearchResult
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.constant.common_words import COMMON_WORDS_LIST
from epstein_files.util.data import Timer, flatten
from epstein_files.util.env import args, logger, specified_names
from epstein_files.util.file_helper import WORD_COUNT_HTML_PATH
from epstein_files.util.rich import (console, highlighter, print_centered, print_page_title, print_panel,
     print_starred_header, write_html)
from epstein_files.util.word_count import WordCount

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
epstein_files = EpsteinFiles.get_files()
emails = flatten([epstein_files.emails_for(n) for n in specified_names]) if specified_names else epstein_files.emails
imessage_logs = epstein_files.imessage_logs_for(specified_names) if specified_names else []
word_count = WordCount()

for email in emails:
    logger.info(f"Counting words in {email}")

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

for imessage_log in imessage_logs:
    logger.info(f"Counting words in {email}")

    for msg in imessage_log.messages():
        if msg.text.startswith('http') or len(msg.text) == 0:
            continue

        for word in msg.text.split():
            word_count.count_word(word, SearchResult(imessage_log, [line]))

print_starred_header(f"Most Common Words in the {len(epstein_files.emails):,} Emails")
print_centered(f"(excluding {len(COMMON_WORDS_LIST)} particularly common words at bottom)", style='dim')
console.line()
console.print(word_count)
console.line(3)
print_panel(f"{len(COMMON_WORDS_LIST):,} Excluded Words")
console.print(', '.join(COMMON_WORDS_LIST), highlight=False)
write_html(WORD_COUNT_HTML_PATH)
timer.print_at_checkpoint(f"Finished counting words")
