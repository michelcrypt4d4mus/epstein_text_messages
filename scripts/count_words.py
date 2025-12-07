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
from epstein_files.util.rich import (console, print_abbreviations_table, print_centered, print_color_key, print_page_title, print_panel,
     print_starred_header, write_html)
from epstein_files.util.word_count import WordCount


timer = Timer()
epstein_files = EpsteinFiles.get_files()
emails = epstein_files.valid_emails()
imessage_logs = epstein_files.imessage_logs_for(specified_names) if specified_names else epstein_files.imessage_logs
word_count = WordCount()
email_subjects: set[str] = set()

for email in emails:
    logger.info(f"Counting words in {email}\n  [SUBJECT] {email.subject()}")
    lines = email.actual_text.split('\n')

    if email.subject() not in email_subjects and f'Re: {email.subject()}' not in email_subjects:
        email_subjects.add(email.subject())
        lines.append(email.subject())

    for line in lines:
        if line.startswith('http') or '#yiv' in line:
            continue

        for word in line.split():
            word_count.count_word(word, SearchResult(email, [line]))

for imessage_log in imessage_logs:
    logger.info(f"Counting words in {imessage_log}")

    for msg in imessage_log.messages():
        if len(specified_names) > 0 and msg.author not in specified_names:
            continue

        if msg.text.startswith('http'):
            continue

        for word in msg.text.split():
            word_count.count_word(word, SearchResult(imessage_log, [msg.text]))

print_page_title(expand=False)
print_starred_header(f"Most Common Words in {len(emails):,} Emails and {len(imessage_logs)} iMessage Logs")
print_centered(f"(excluding {len(COMMON_WORDS_LIST)} particularly common words at bottom)", style='dim')
# print_abbreviations_table()
console.line()
console.print(word_count)
console.line()
print_color_key()
console.line(2)
print_panel(f"{len(COMMON_WORDS_LIST):,} Excluded Words", centered=True)
console.print(', '.join(COMMON_WORDS_LIST), highlight=False)
write_html(WORD_COUNT_HTML_PATH)
timer.print_at_checkpoint(f"Finished counting words")
