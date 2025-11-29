import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

from rich.align import Align
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from documents.document import Document
from documents.email import DETECT_EMAIL_REGEX, USELESS_EMAILERS, Email
from documents.email_header import AUTHOR
from documents.messenger_log import MSG_REGEX, MessengerLog
from util.constants import *
from util.data import flatten, patternize
from util.env import args, is_debug, logger
from util.file_helper import DOCS_DIR, move_json_file
from util.rich import console, get_style_for_name, highlight_text, make_link, make_link_markup, print_author_header, print_panel, vertically_pad

DEVICE_SIGNATURE = 'Device Signature'
DEVICE_SIGNATURE_PADDING = (0, 0, 0, 2)
NOT_INCLUDED_EMAILERS = [e.lower() for e in (USELESS_EMAILERS + [JEFFREY_EPSTEIN])]


@dataclass
class EpsteinFiles:
    all_files: list[Path] = field(init=False)
    emails: list[Email] = field(default_factory=list)
    imessage_logs: list[MessengerLog] = field(default_factory=list)
    other_files: list[Document] = field(default_factory=list)
    email_author_counts: dict[str, int] = field(init=False)
    email_author_device_signatures: dict[str, set[str]] = field(init=False)
    email_recipient_counts: dict[str, int] = field(init=False)
    email_sent_from_devices: dict[str, set[str ]] = field(init=False)
    email_unknown_recipient_file_ids: set[str] = field(default_factory=set)

    def __post_init__(self):
        self.all_files = [f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]
        self.email_author_counts = defaultdict(int)
        self.email_author_device_signatures = defaultdict(set)
        self.email_recipient_counts = defaultdict(int)
        self.email_sent_from_devices = defaultdict(set)

        for file_arg in self.all_files:
            if is_debug:
                console.print(f"\nScanning '{file_arg.name}'...")

            document = Document(file_arg)

            if document.length == 0:
                logger.info('Skipping empty file...')
            elif document.text[0] == '{':  # Check for JSON
                move_json_file(file_arg)
            elif MSG_REGEX.search(document.text):
                logger.info('iMessage log file...')
                self.imessage_logs.append(MessengerLog(file_arg))
            elif DETECT_EMAIL_REGEX.match(document.text) or document.file_id in KNOWN_EMAIL_AUTHORS:  # Handle emails
                email = Email(file_arg)
                self.emails.append(email)
                author = email.author or UNKNOWN
                self.email_author_counts[author] += 1
                logger.info(email.description().plain)
                recipients = [UNKNOWN] if len(email.recipients) == 0 else [r or UNKNOWN for r in email.recipients]

                for recipient in recipients:
                    self.email_recipient_counts[recipient] += 1

                if UNKNOWN in email.recipients:
                    self.email_unknown_recipient_file_ids.add(email.file_id)

                if email.sent_from_device:
                    self.email_author_device_signatures[email.author or UNKNOWN].add(email.sent_from_device)
                    self.email_sent_from_devices[email.sent_from_device].add(author)

                if len(author) <= 3 or author == UNKNOWN:
                    email.log_top_lines(msg=f"Redacted or invalid email author '{author}'")
            else:
                logger.info('Unknown file type...')
                self.other_files.append(document)
                document.log_top_lines()

        self.imessage_logs = sorted(self.imessage_logs, key=lambda f: f.timestamp)

    def all_documents(self) -> list[Document]:
        return self.imessage_logs + self.emails + self.other_files

    def all_emailers(self, include_useless: bool = False) -> list[str]:
        """Returns all emailers except Epstein and USELESS_EMAILERS, sorted from least frequent to most."""
        emailers = [a for a in self.email_author_counts.keys()] + [r for r in self.email_recipient_counts.keys()]
        emailers = emailers if include_useless else [e for e in emailers if e.lower() not in NOT_INCLUDED_EMAILERS]
        return sorted(list(set(emailers)), key=lambda e: self.email_author_counts[e] + self.email_recipient_counts[e])

    def all_emailer_counts(self) -> dict[str, int]:
        return {e: self.email_author_counts[e] + self.email_recipient_counts[e] for e in self.all_emailers(True)}

    def earliest_email_at(self, author: str | None) -> datetime:
        return self.emails_for(author)[0].timestamp

    def emails_for(self, author: str | None) -> list[Email]:
        """Returns emails to or from a given 'author' sorted chronologically."""
        author = author.lower() if (author and author != UNKNOWN) else None
        emails_by = [e for e in self.emails if e.author_lowercase == author]
        emails_to = []

        if author is None:
            emails_to = [
                e for e in self.emails
                if e.author == JEFFREY_EPSTEIN and (len(e.recipients) == 0 or None in e.recipients or UNKNOWN in e.recipients)
            ]
        else:
            emails_to = [e for e in self.emails if author in e.recipients_lower]

        sorted_emails = EpsteinFiles.sort_emails(emails_by + emails_to)

        if len(sorted_emails) == 0:
            logger.warning(f"No emails found for '{author}'")

        return sorted_emails

    def identified_imessage_log_count(self) -> int:
        return len([log for log in self.imessage_logs if log.author])

    def imessage_msg_count(self) -> int:
        return sum([log.msg_count for log in self.imessage_logs])

    def num_identified_email_authors(self) -> int:
        return sum([i for author, i in self.email_author_counts.items() if author != UNKNOWN])

    def print_emails_for(self, _author: str | None) -> None:
        """Print complete emails to or from a particular 'author'."""
        emails = self.emails_for(_author)
        author = _author or UNKNOWN
        logger.info(f"print_emails_for({author}) [_author{_author}]")

        if len(emails) > 0:
            print_author_header(
                f"Found {len(emails)} {author} emails from {emails[0].timestamp.date()} to {emails[-1].timestamp.date()}",
                get_style_for_name(author)
            )
        else:
            raise RuntimeError(f"No emails found for '{_author}'")

        if author != UNKNOWN:
            self.print_emails_table_for(author)
        else:
            ids = list(self.email_unknown_recipient_file_ids)
            logger.info(f"{len(ids)} UNKNOWN RECIPIENT IDS:\n" + '\n'.join(sorted(ids)))

        for email in emails:
            console.print(email)

    def print_emails_table_for(self, author: str) -> None:
        emails = self.emails_for(author)
        table_title = f"Emails to/from {author} starting {emails[0].timestamp.date()}"
        table = Table(title=table_title, show_header=True, header_style="bold")
        table.add_column("From", justify="left")
        table.add_column("Date", justify="center")
        table.add_column("Subject", justify="left", style='honeydew2', min_width=35)

        for email in emails:
            table.add_row(
                email.author_txt,
                email.epsteinify_link(link_txt=email.timestamp_without_seconds()),
                highlight_text(email.header.subject or '')
            )

        console.print(table, '\n')

    def print_email_device_info(self) -> None:
        print_panel(f"Email [italic]Sent from \\[DEVICE][/italic] Signature Breakdown", padding=DEVICE_SIGNATURE_PADDING)
        console.print(build_signature_table(self.email_author_device_signatures, (AUTHOR, DEVICE_SIGNATURE)))
        console.line(2)
        console.print(build_signature_table(self.email_sent_from_devices, (DEVICE_SIGNATURE, AUTHOR), ', '))
        console.line(2)

    def print_emailer_counts_table(self) -> None:
        counts_table = Table(title=f"Email Counts", show_header=True, header_style="bold")
        counts_table.add_column('Name', justify="left", style='white')
        counts_table.add_column('Jmail', justify="center")
        counts_table.add_column("Total", justify="center")
        counts_table.add_column("Sent", justify="center")
        counts_table.add_column("Received", justify="center")
        sort_key = lambda item: item[0] if args.sort_alphabetical else [item[1], item[0]]

        for k, count in sorted(self.all_emailer_counts().items(), key=sort_key, reverse=True):
            counts_table.add_row(
                Text.from_markup(make_link_markup(epsteinify_name_url(k), k, get_style_for_name(k, 'grey82'))),
                make_link(jmail_search_url(k), 'Search Jmail'),
                str(count),
                str(self.email_author_counts[k]),
                str(self.email_recipient_counts[k])
            )

        console.print(vertically_pad(counts_table))

    def print_other_files_table(self) -> None:
        table = Table(header_style="bold", show_header=True, show_lines=True)
        table.add_column("File", justify="left")
        table.add_column("Length", justify="center")
        table.add_column("First Few Lines", justify="left", style='pale_turquoise4')

        for doc in sorted(self.other_files, key=lambda document: document.filename):
            table.add_row(doc.epsteinify_link_markup, f"{doc.length:,}", doc.highlighted_preview_text())

        console.print(table)

    def print_summary(self) -> None:
        table = Table(title=f"File Analysis Summary", show_header=True, header_style="bold")
        table.add_column("File Type", justify='left')
        table.add_column("File Count", justify='center')
        table.add_column("Known Author Count", justify='center')
        table.add_row('iMessage Logs', f"{len(self.imessage_logs):,}", str(self.identified_imessage_log_count()))
        table.add_row('Emails', f"{len(self.emails):,}", f"{len([e for e in self.emails if e.author]):,}")
        table.add_row('Other', f"{len(self.other_files):,}", 'n/a')
        console.print(Padding(Align.center(table), (0, 0, 1, 0)))

    def lines_matching(self, _pattern: re.Pattern | str, file_type: Literal['all', 'other'] = 'all') -> list[str | Text]:
        documents = self.all_documents() if file_type == 'all' else self.other_files
        return flatten([doc.lines_matching_txt(patternize(_pattern)) for doc in documents])

    @staticmethod
    def sort_emails(emails: list[Email]) -> list[Email]:
        return sorted(emails, key=lambda email: email.timestamp)


def build_signature_table(keyed_sets: dict[str, set[str]], cols: tuple[str, str], join_char: str = '\n') -> Padding:
    title = 'Signatures Used By Authors' if cols[0] == AUTHOR else 'Authors Seen Using Signatures'
    table = Table(header_style="bold reverse", show_header=True, show_lines=True, title=title)

    for i, col in enumerate(cols):
        table.add_column(col.title() + ('s' if i == 1 else ''), style='dim' if col == DEVICE_SIGNATURE else 'white')

    new_dict: dict[str, list[str]] = {}

    for k, v in keyed_sets.items():
        new_dict[k] = list(v)

    for k in sorted(new_dict.keys()):
        _list = new_dict[k]
        table.add_row(highlight_text(k or UNKNOWN), highlight_text(join_char.join(sorted(_list))))

    return Padding(table, DEVICE_SIGNATURE_PADDING)
