import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

from rich.align import Align
from rich.markup import escape
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from epstein_files.documents.document import Document, SearchResult
from epstein_files.documents.email import DETECT_EMAIL_REGEX, JUNK_EMAILERS, KRASSNER_RECIPIENTS, USELESS_EMAILERS, Email
from epstein_files.documents.email_header import AUTHOR
from epstein_files.documents.messenger_log import MSG_REGEX, MessengerLog, sender_counts
from epstein_files.util.constant.urls import EPSTEIN_WEB, JMAIL, epsteinify_name_url, epstein_web_person_url, search_jmail_url, search_twitter_url
from epstein_files.util.constants import *
from epstein_files.util.data import dict_sets_to_lists, patternize
from epstein_files.util.env import args, is_debug, logger
from epstein_files.util.file_helper import DOCS_DIR, move_json_file
from epstein_files.util.highlighted_group import get_info_for_name, get_style_for_name
from epstein_files.util.rich import (DEFAULT_NAME_COLOR, console, highlighter, link_text_obj, link_markup,
     print_author_header, print_panel, vertically_pad)

DEVICE_SIGNATURE = 'Device Signature'
DEVICE_SIGNATURE_PADDING = (0, 0, 0, 2)
NOT_INCLUDED_EMAILERS = [e.lower() for e in (USELESS_EMAILERS + [JEFFREY_EPSTEIN])]


@dataclass
class EpsteinFiles:
    all_files: list[Path] = field(init=False)
    emails: list[Email] = field(default_factory=list)
    imessage_logs: list[MessengerLog] = field(default_factory=list)
    other_files: list[Document] = field(default_factory=list)
    # Analytics / calculations
    email_author_counts: dict[str | None, int] = field(default_factory=lambda: defaultdict(int))
    email_authors_to_device_signatures: dict[str, set] = field(default_factory=lambda: defaultdict(set))
    email_device_signatures_to_authors: dict[str, set] = field(default_factory=lambda: defaultdict(set))
    email_recipient_counts: dict[str | None, int] = field(default_factory=lambda: defaultdict(int))
    _email_unknown_recipient_file_ids: set[str] = field(default_factory=set)

    def __post_init__(self):
        self.all_files = [f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]

        for file_arg in self.all_files:
            logger.debug(f"\nScanning '{file_arg.name}'...")
            document = Document(file_arg)

            if document.length == 0:
                logger.info(f'{file_arg.name}: Skipping empty file...')
            elif document.text[0] == '{':  # Check for JSON
                move_json_file(file_arg)
            elif MSG_REGEX.search(document.text):
                logger.info(f'{file_arg.name}: iMessage log file...')
                self.imessage_logs.append(MessengerLog(file_arg))
            elif DETECT_EMAIL_REGEX.match(document.text) or document.file_id in KNOWN_EMAIL_AUTHORS:  # Handle emails
                email = Email(file_arg, text=document.text)  # Avoid reloads
                logger.info(f"{file_arg.name}: {email.description().plain}")
                self.emails.append(email)
                self.email_author_counts[email.author] += 1

                if len(email.recipients) == 0:
                    self._email_unknown_recipient_file_ids.add(email.file_id)
                    self.email_recipient_counts[None] += 1
                else:
                    for recipient in email.recipients:
                        self.email_recipient_counts[recipient] += 1

                if email.sent_from_device:
                    self.email_authors_to_device_signatures[email.author_or_unknown()].add(email.sent_from_device)
                    self.email_device_signatures_to_authors[email.sent_from_device].add(email.author_or_unknown())
            else:
                logger.info('Unknown file type...')
                self.other_files.append(document)

        self.imessage_logs = sorted(self.imessage_logs, key=lambda f: f.timestamp)
        self.identified_imessage_log_count = len([log for log in self.imessage_logs if log.author])

    def all_documents(self) -> list[Document]:
        return self.imessage_logs + self.emails + self.other_files

    def all_emailers(self, include_useless: bool = False) -> list[str | None]:
        """Returns all emailers except Epstein and USELESS_EMAILERS, sorted from least frequent to most."""
        names = [a for a in self.email_author_counts.keys()] + [r for r in self.email_recipient_counts.keys()]
        names = names if include_useless else [e for e in names if e is None or e.lower() not in NOT_INCLUDED_EMAILERS]
        return sorted(list(set(names)), key=lambda e: self.email_author_counts[e] + self.email_recipient_counts[e])

    def attributed_email_count(self) -> int:
        return sum([i for author, i in self.email_author_counts.items() if author != UNKNOWN])

    def docs_matching(self, _pattern: re.Pattern | str, file_type: Literal['all', 'other'] = 'all') -> list[SearchResult]:
        results: list[SearchResult] = []

        for doc in (self.all_documents() if file_type == 'all' else self.other_files):
            lines = doc.lines_matching_txt(patternize(_pattern))

            if len(lines) > 0:
                results.append(SearchResult(doc, lines))

        return results

    def earliest_email_at(self, author: str | None) -> datetime:
        return self.emails_for(author)[0].timestamp

    def last_email_at(self, author: str | None) -> datetime:
        return self.emails_for(author)[-1].timestamp

    def email_conversation_length_in_days(self, author: str | None) -> int:
        return (self.last_email_at(author) - self.earliest_email_at(author)).days + 1

    def email_unknown_recipient_file_ids(self) -> list[str]:
        return sorted(list(self._email_unknown_recipient_file_ids))

    def emails_for(self, author: str | None) -> list[Email]:
        """Returns emails to or from a given 'author' sorted chronologically."""
        emails_by = [e for e in self.emails if e.author == author]

        # Only emails from Epstein to unknown/redacted recipients should be returned when getting emails_for(None)
        if author is None:
            emails_to = [e for e in self.emails if e.author == JEFFREY_EPSTEIN and len(e.recipients) == 0]
        else:
            emails_to = [e for e in self.emails if author in e.recipients]

        if len(emails_by) == 0 and len(emails_to) == 0:
            raise RuntimeError(f"No emails found for '{author}'")

        return EpsteinFiles.sort_emails(emails_by + emails_to)

    def print_files_overview(self) -> None:
        table = Table(title=f"File Analysis Summary", header_style="bold")
        table.add_column("File Type", justify='left')
        table.add_column("File Count", justify='center')
        table.add_column("Known Author Count", justify='center')
        table.add_row('iMessage Logs', f"{len(self.imessage_logs):,}", str(self.identified_imessage_log_count))
        table.add_row('Emails', f"{len(self.emails):,}", f"{len([e for e in self.emails if e.author]):,}")
        table.add_row('Other', f"{len(self.other_files):,}", 'n/a')
        console.print(Padding(Align.center(vertically_pad(table))))

    def print_emails_for(self, _author: str | None) -> int:
        """Print complete emails to or from a particular 'author'. Returns number of emails printed."""
        conversation_length = self.email_conversation_length_in_days(_author)
        emails = self.emails_for(_author)
        author = _author or UNKNOWN

        print_author_header(
            f"Found {len(emails)} {author} emails starting {emails[0].timestamp.date()} over {conversation_length:,} days",
            get_style_for_name(author),
            get_info_for_name(author)
        )

        self.print_emails_table_for(_author)

        for email in emails:
            console.print(email)

        return len(emails)

    def print_emails_table_for(self, _author: str | None) -> None:
        emails = self.emails_for(_author)
        author = _author or UNKNOWN

        table = Table(
            title=f"Emails to/from {author} starting {emails[0].timestamp.date()}",
            border_style=get_style_for_name(author, allow_bold=False),
            header_style="bold"
        )

        table.add_column('From', justify='left')
        table.add_column('Timestamp', justify='center')
        table.add_column('Subject', justify='left', style='honeydew2', min_width=60)

        for email in emails:
            table.add_row(
                email.author_txt,
                email.epsteinify_link(link_txt=email.timestamp_without_seconds()),
                highlighter(email.header.subject or '')
            )

        console.print(Align.center(table), '\n')

    def print_email_device_info(self) -> None:
        print_panel(f"Email [italic]Sent from \\[DEVICE][/italic] Signature Breakdown", padding=(0, 0, 0, 11))
        console.print(build_signature_table(self.email_authors_to_device_signatures, (AUTHOR, DEVICE_SIGNATURE)))
        console.line(2)
        console.print(build_signature_table(self.email_device_signatures_to_authors, (DEVICE_SIGNATURE, AUTHOR), ', '))
        console.line(2)

    def print_emailer_counts_table(self) -> None:
        footer = f"Identified authors of {self.attributed_email_count()} emails out of {len(self.emails)} potential email files."
        counts_table = Table(title=f"Email Counts", caption=footer, header_style="bold")

        for i, col in enumerate(['Name', 'Count', 'Sent', "Recv'd", JMAIL, EPSTEIN_WEB, 'Twitter']):
            counts_table.add_column(col, justify='left' if i == 0 else 'center')

        emailer_counts = {e: self.email_author_counts[e] + self.email_recipient_counts[e] for e in self.all_emailers(True)}
        sort_key = lambda item: item[0] if args.sort_alphabetical else [item[1], item[0]]

        for p, count in sorted(emailer_counts.items(), key=sort_key, reverse=True):
            style = get_style_for_name(p, DEFAULT_NAME_COLOR)

            counts_table.add_row(
                Text.from_markup(link_markup(epsteinify_name_url(p or UNKNOWN), p or UNKNOWN, style)),
                str(count),
                str(self.email_author_counts[p]),
                str(self.email_recipient_counts[p]),
                '' if p is None else link_text_obj(search_jmail_url(p), JMAIL),
                '' if not is_ok_for_epstein_web(p) else link_text_obj(epstein_web_person_url(p), EPSTEIN_WEB.lower()),
                '' if p is None else link_text_obj(search_twitter_url(p), 'search X'),
            )

        console.print(vertically_pad(counts_table, 2))

    def print_imessage_summary(self) -> None:
        """Print summary table and stats for text messages."""
        counts_table = Table(title="Text Message Counts By Author", header_style="bold")
        counts_table.add_column(AUTHOR.title(), style="steel_blue bold", justify='left', width=30)
        counts_table.add_column("Message Count", justify='center')

        for k, v in sorted(sender_counts.items(), key=lambda item: item[1], reverse=True):
            counts_table.add_row(Text(k, get_style_for_name(k)), str(v))

        console.print(counts_table)
        text_summary_msg = f"\nDeanonymized {self.identified_imessage_log_count} of "
        text_summary_msg += f"{len(self.imessage_logs)} text msg logs found in {len(self.all_files)} files."
        console.print(text_summary_msg)
        imessage_msg_count = sum([log.msg_count for log in self.imessage_logs])
        console.print(f"Found {imessage_msg_count} total text messages in {len(self.imessage_logs)} conversations.")
        console.print(f"(Last deploy found 4668 messages in 77 conversations)", style='dim')

    def print_other_files_table(self) -> None:
        table = Table(header_style='bold', show_lines=True)
        table.add_column('File', justify='left')
        table.add_column('Length', justify='center')
        table.add_column('First Few Lines', justify='left', style='pale_turquoise4')

        for doc in sorted(self.other_files, key=lambda document: document.filename):
            table.add_row(doc.raw_document_link_txt(), f"{doc.length:,}", doc.highlighted_preview_text())

        console.print(table)

    @staticmethod
    def sort_emails(emails: list[Email]) -> list[Email]:
        return sorted(emails, key=lambda email: email.timestamp)


def build_signature_table(keyed_sets: dict[str, set[str]], cols: tuple[str, str], join_char: str = '\n') -> Padding:
    title = 'Signatures Used By Authors' if cols[0] == AUTHOR else 'Authors Seen Using Signatures'
    table = Table(header_style="bold reverse", show_lines=True, title=title)

    for i, col in enumerate(cols):
        table.add_column(col.title() + ('s' if i == 1 else ''))

    new_dict = dict_sets_to_lists(keyed_sets)

    for k in sorted(new_dict.keys()):
        _list = new_dict[k]
        table.add_row(highlighter(k or UNKNOWN), highlighter(join_char.join(sorted(_list))))

    return Padding(table, DEVICE_SIGNATURE_PADDING)


def is_ok_for_epstein_web(name: str | None) -> bool:
    if name is None:
        return False
    if '@' in name or '/' in name or name in JUNK_EMAILERS or name in KRASSNER_RECIPIENTS or name == UNKNOWN:
        return False
    elif name in ['ACT for America'] or ' ' not in name:
        return False
    else:
        return True
