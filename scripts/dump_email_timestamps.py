#!/usr/bin/env python
# Print email ID + timestamp
import logging
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
from epstein_files.output.highlight_config import HIGHLIGHTED_NAMES, get_style_for_name
from epstein_files.output.highlighted_names import HighlightedNames
from epstein_files.util.constant.names import *
from epstein_files.util.constants import CONFIGS_BY_ID, EmailCfg
from epstein_files.util.helpers.data_helpers import *
from epstein_files.util.helpers.string_helper import quote
from epstein_files.util.logging import logger
from epstein_files.output.rich import console, highlighter, print_json, print_subtitle_panel


for cfg in CONFIGS_BY_ID.values():
    if isinstance(cfg, EmailCfg) and not cfg.description:
        continue

    txt = Text('').append(cfg.category_txt).append(f"{cfg.id} interesting? {cfg.is_of_interest}, ")
    txt.append(f"complete_description=", 'grey').append(quote(cfg.complete_description), style='wheat4')
    # console.print(txt)
    logger.warning(txt.plain)
    logger.warning(repr(cfg))
    # console.print(cfg.__rich__().plain)

    # if cfg.is_of_interest:
    #     console.line()
        # console.print(repr(cfg))

    console.line(2)

# # Print all DOJ files from biggest to smallest.
# for i, doc in enumerate(sorted(epstein_files.doj_files, key=lambda f: -f.length)):
#     # txt = Text('').append(Text('interesting', style='green') if doc.is_interesting else Text('not interesting', style='red'))
#     # console.print(txt.append(': ') + doc.summary)
#     console.print(doc)

sys.exit()


# Look for possible email files in the DOJ files
with open('timestamps_cfg.txt', 'wt') as f:
    emails = []

    for i, doc in enumerate(sorted(epstein_files.doj_files, key=lambda f: -f.length)):
        cls = document_cls(doc)

        if cls == Email:
            try:
                email = Email(doc.file_path)
                console.print(email)
                emails.append(email)
            except Exception as e:
                logger.error(f"Failed to turn {doc} into an email ({e})")

                if doc.timestamp:
                    f.write(f"    EmailCfg(id='{doc.file_id}', date='{doc.timestamp}'),\n")
                    logger.warning(f"Wrote EmailCfg line with timestamp {doc.timestamp}...")
        else:
            logger.warning(f"{doc.file_id}: {doc.file_size_str} ({doc.length:,} bytes) is not an Email...")

console.print(f"Found {len(emails)} emails out of {len(epstein_files.doj_files)} DOJ files.")
sys.exit()


# Show biggest files
for i, doc in enumerate(sorted(epstein_files.doj_files, key=lambda f: -f.length)):
    console.print(f"{doc.file_id}: {doc.file_size_str} ({doc.length:,} bytes)")

    if i > 2000:
        break


sys.exit()

for email in epstein_files.non_duplicate_emails:
    if email._is_first_for_user:
        print(f"{email}, _is_first_for_user={email._is_first_for_user}")


sys.exit()


def print_first_emails():
    emailers = sorted(epstein_files.emailers, key=lambda e: e.earliest_email_at)

    for emailer in emailers:
        first_email = emailer.emails[0]

        if emailer.is_uninteresting or first_email.is_fwded_article:
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

    for highlight in HIGHLIGHTED_NAMES:
        if type(highlight) != HighlightedNames:
            continue
        elif not highlight.should_match_first_last_name:
            continue

        for name in highlight.emailers:
            for partial_name in [n.lower() for n in [extract_first_name(name), extract_last_name(name)]]:
                partial_name_counts[partial_name] += 1

                if partial_name not in NAMES_TO_NOT_HIGHLIGHT:
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

# for doc in sorted(epstein_files.all_documents, key=lambda e: e.file_id):
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
        console.print(Panel(email.summary, expand=False, style=email.border_style))
        console.print(escape(email._extract_actual_text()))

console.line(2)

for i, id_count in enumerate(sort_dict(max_sizes)):
    if i > 50:
        continue

    id = id_count[0]
    count = id_count[1]
    email = epstein_files.get_ids([id])[0]
    console.print(f"{count:6d}: {email.summary.plain}")


console.line(2)
console.print('counts', counts)
