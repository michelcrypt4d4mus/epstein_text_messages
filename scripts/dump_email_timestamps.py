#!/usr/bin/env python
# Print email ID + timestamp
import sys
from collections import defaultdict

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from scripts.use_pickled import console, epstein_files
from epstein_files.epstein_files import document_cls
from epstein_files.documents.document import Document
from epstein_files.documents.email import Email, UNINTERESTING_EMAILERS
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import HIGHLIGHT_GROUPS, get_style_for_name
from epstein_files.output.highlighted_names import HighlightedNames
from epstein_files.output.html.builder import table_to_html, write_templated_html
from epstein_files.people.person import Person
from epstein_files.people.names import *
from epstein_files.util.constants import CONFIGS_BY_ID, EmailCfg
from epstein_files.util.helpers.data_helpers import *
from epstein_files.util.helpers.debugging_helper import print_all_timestamps, print_file_counts
from epstein_files.util.helpers.file_helper import open_file_or_url
from epstein_files.util.helpers.string_helper import extract_emojis, quote
from epstein_files.util.logging import logger
from epstein_files.output.rich import bool_txt, console, highlighter, print_subtitle_panel


num_missing_unknown_recipient = 0
num_interesting = 0
num_uninteresting = 0
num_word_count_worthy = 0
ids = []

for i, email in enumerate(epstein_files.unique_emails):
    # if email._config.recipients or not email.is_word_count_worthy or email.author == CHRISTOPHER_DILORIO:
    if email._config.recipients:
        continue

    if (email.header.has_empty_to_header or email.header.has_empty_cc_header) and None not in email.recipients_real:
        if email.author == CHRISTOPHER_DILORIO:
            email._warn(f"skipping dilorio email...")
            continue

        ids.append(email.file_id)
        num_missing_unknown_recipient += 1
        num_word_count_worthy += int(email.is_word_count_worthy)
        email._warn(f"empty To: header but None is not in recipients_real (is_interesting={email.is_interesting})")

        if email.is_interesting is False:
            email._warn(f"considered uninteresting...")
            console.print(email._summary, '\n')
            num_interesting += 1
            continue
        elif email.is_interesting is True:
            num_interesting += 1
            email._warn(f"not showing contents because it's already considered interesting...")
            console.print(email._summary, '\n')
            continue

        console.line()
        console.print(email)
        console.print(email.header)
        console.line()


console.print(f'\n\n  Found {num_missing_unknown_recipient} emails that should have None as a recipient ({num_interesting} interesting, {num_uninteresting} uninteresting)')
console.print(f"\nIDS to repair:\n\n" + ' '.join(ids) + '\n')
sys.exit()



for email in epstein_files.unique_emails:
    if email.is_persons_first_email:
        print(f"{email}, is_persons_first_email={email.is_persons_first_email}")


sys.exit()


def print_first_emails():
    emailers = sorted(epstein_files.emailers, key=lambda e: e.earliest_email_at)

    for emailer in emailers:
        first_email = emailer.emails[0]

        if emailer.is_interesting or first_email.is_fwded_article:
            continue
        elif first_email._truncate_to_length() >= first_email.length:
            logger.warning(f"User '{emailer.name}' first email is untruncated")
            continue
        elif emailer.should_always_truncate:
            logger.warning(f"Skipping truncatable user '{emailer.name}'")
            continue

        print_subtitle_panel(emailer.name_str)
        console.print(emailer.emails[0])

print_first_emails()
sys.exit()


def print_partial_names_used_in_regexes():
    names = []
    partial_name_counts = defaultdict(int)

    for highlight in HIGHLIGHT_GROUPS:
        if type(highlight) != HighlightedNames:
            continue
        elif not highlight.should_match_first_last_name:
            continue

        for name in highlight.contacts:
            for partial_name in [n.lower() for n in [extract_first_name(name), extract_last_name(name)]]:
                partial_name_counts[partial_name] += 1

                if partial_name not in NAMES_TO_NOT_PARTIALLY_MATCH:
                    names.append(partial_name)
                    print(f"name='{name}', partial_name='{partial_name}'")

    print('\n'.join(sorted(names)))
    print(f"\n\n")

    for name, count in partial_name_counts.items():
        if count > 1:
            print(f"partial name '{name}' appears {count} times")

    sys.exit()


print_partial_names_used_in_regexes()
max_sizes = defaultdict(int)
counts = defaultdict(int)

# for doc in sorted(epstein_files.documents, key=lambda e: e.file_id):
#     max_file_sizes[doc.class_name()] = max(max_file_sizes[doc.class_name()], doc.file_size())
#     console.print(doc.summary)
#     print_json('metadata', doc.metadata())


def print_potential_uninteresting_emailers():
    emailers = sorted(epstein_files.emailers, key=lambda e: epstein_files.earliest_email_at(e.name))

    for emailer in emailers:
        emails = emailer.emails
        emails_sent_by = [e for e in emails if e.author == emailer]
        emailer_str = f"(useless emailer) {emailer}" if emailer in UNINTERESTING_EMAILERS else emailer
        txt = Text('')

        if len(emails) == 1:
            if len(emails_sent_by) == 1:
                console.print(txt.append('     [SENT ONE]', style='bright_green dim').append(highlighter(f" {emailer_str} ({len(emails[0].recipients)} recipients)")))
            else:
                console.print(txt.append(' [RECEIVED ONE]', style='bright_red dim').append(highlighter(f" {emailer_str} ({len(emails[0].recipients)} recipients)")))
        elif len(emails_sent_by) == 0:
            console.print(txt.append('    [NONE SENT]', style='dim').append(highlighter(f" {emailer_str} received {len(emails)} emails but sent none")))
        elif get_style_for_name(emailer.name, default_style='none') == 'none':
            console.print(Text('     [NO STYLE]', style='wheat4').append(highlighter(f" {emailer_str} has no associated styling")))


print_potential_uninteresting_emailers()
sys.exit()
counts = defaultdict(int)


for email in sorted(epstein_files.emails, key=lambda e: -len(e.actual_text)):
    if email.is_fwded_article or email.is_mailing_list or email.is_duplicate:
        if email.is_fwded_article:
            counts['fwd'] += 1
        elif email.is_mailing_list:
            counts['mailing_list'] += 1
        elif email.is_duplicate:
            counts['dupe'] += 1

        continue

    if len(email.actual_text) > 100:
        max_sizes[email.file_id] = len(email.actual_text)
        console.line(2)
        console.print(Panel(email._summary, expand=False, style=email.border_style))
        console.print(escape(email._extract_actual_text()))

console.line(2)

for i, id_count in enumerate(sort_dict(max_sizes)):
    if i > 50:
        continue

    id = id_count[0]
    count = id_count[1]
    email = epstein_files.get_ids([id])[0]
    console.print(f"{count:6d}: {email._summary.plain}")


console.line(2)
console.print('counts', counts)
