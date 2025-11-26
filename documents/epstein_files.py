import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from rich.align import Align
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text

from documents.document import Document
from documents.email import DETECT_EMAIL_REGEX, Email
from documents.email_header import AUTHOR
from documents.messenger_log import MSG_REGEX, MessengerLog
from util.constants import *
from util.env import is_debug
from util.file_helper import DOCS_DIR, move_json_file
from util.rich import COUNTERPARTY_COLORS, console, highlight_text, logger, print_panel

DEVICE_SIGNATURE = 'Device Signature'
DEVICE_SIGNATURE_PADDING = (0, 0, 0, 2)


@dataclass
class EpsteinFiles:
    all_files: list[Path] = field(init=False)
    emails: list[Email] = field(default_factory=list)
    iMessage_logs: list[MessengerLog] = field(default_factory=list)
    other_files: list[Document] = field(default_factory=list)
    email_author_counts: dict[str, int] = field(init=False)
    email_recipient_counts: dict[str, int] = field(init=False)
    email_sent_from_devices: dict[str, set[str ]] = field(default_factory=dict)
    email_author_devices: dict[str, set[str]] = field(default_factory=dict)
    email_unknown_recipient_ids: set[str] = field(default_factory=set)

    def __post_init__(self):
        self.all_files = [f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]
        self.email_author_counts = defaultdict(int)
        self.email_recipient_counts = defaultdict(int)
        self.email_author_devices = defaultdict(set)
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
                self.iMessage_logs.append(MessengerLog(file_arg))
            elif DETECT_EMAIL_REGEX.match(document.text) or document.file_id in KNOWN_EMAIL_AUTHORS:  # Handle emails
                email = Email(file_arg)
                self.emails.append(email)
                author = email.author or UNKNOWN
                self.email_author_counts[author.lower()] += 1
                logger.info(email.description().plain)

                if len(email.recipients) > 0:
                    for recipient in email.recipients:
                        self.email_recipient_counts[recipient.lower() if recipient else UNKNOWN] += 1
                else:
                    self.email_recipient_counts[UNKNOWN] += 1

                if None in email.recipients or UNKNOWN in email.recipients or len(email.recipients) == 0:
                    self.email_unknown_recipient_ids.add(email.file_id)

                if email.sent_from_device:
                    self.email_author_devices[email.author or UNKNOWN].add(email.sent_from_device)
                    self.email_sent_from_devices[email.sent_from_device].add(author)

                if len(author) <= 3 or author == UNKNOWN:
                    email.log_top_lines(msg=f"Redacted or invalid email author '{author}'")
            else:
                logger.info('Unknown file type...')
                self.other_files.append(document)
                document.log_top_lines()

    def emails_for(self, author: str | None) -> list[Email]:
        """Returns emails to or from a given 'author' sorted chronologically."""
        author = author.lower() if author else None
        emails_by = [e for e in self.emails if e.author_lowercase == author]
        emails_to = []

        if author is None:
            emails_to = [
                e for e in self.emails
                if e.author == JEFFREY_EPSTEIN and (len(e.recipients) == 0 or None in e.recipients or UNKNOWN in e.recipients)
            ]
        else:
            emails_to = [e for e in self.emails if author in e.recipients_lower]

        return EpsteinFiles.sort_emails(emails_by + emails_to)

    def identified_imessage_log_count(self) -> int:
        return len([log for log in self.iMessage_logs if log.author])

    def imessage_msg_count(self) -> int:
        return sum([log.msg_count for log in self.sorted_imessage_logs()])

    def num_identified_email_authors(self) -> int:
        return sum([i for author, i in self.email_author_counts.items() if author != UNKNOWN])

    def print_emails_for(self, author: str | None) -> None:
        """Print complete emails to or from a particular 'author'."""
        emails = self.emails_for(author)
        author = author or UNKNOWN

        if len(emails) > 0:
            txt = Text(f"Found {len(emails)} emails to/from {author}", justify='center')
            panel = Panel(txt, width=80, style=f"bright_white on {COUNTERPARTY_COLORS.get(author, 'default')} bold")
            console.print('\n', Align.center(panel), '\n')
        else:
            logger.warning(f"No emails found for {author}")
            return

        if author is not None and author != UNKNOWN:
            self.print_emails_table_for(author)
        else:
            ids = list(self.email_unknown_recipient_ids)
            logger.info(f"{len(ids)} UNKNOWN RECIPIENT IDS:\n" + '\n'.join(sorted(ids)))

        for email in emails:
            console.print(email)

    def print_emails_table_for(self, author: str) -> None:
        table = Table(title=f"Emails to/from {author}", show_header=True, header_style="bold")
        table.add_column("From", justify="left")
        table.add_column("Date", justify="center")
        table.add_column("Subject", justify="left", style='pale_turquoise4')

        for email in self.emails_for(author):
            table.add_row(
                email.author_txt,
                email.epsteinify_link(link_txt=str(email.sort_time())),
                email.header.subject
            )

        console.print(table, '\n\n')

    def print_email_device_info(self) -> None:
        print_panel(f"Email [italic]Sent from \\[DEVICE][/italic] Signature Breakdown", padding=DEVICE_SIGNATURE_PADDING)
        console.print(build_signature_table(self.email_author_devices, (AUTHOR, DEVICE_SIGNATURE)))
        console.line(2)
        console.print(build_signature_table(self.email_sent_from_devices, (DEVICE_SIGNATURE, AUTHOR), ', '))
        console.line(2)

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
        table.add_column("Deanonymized Count", justify='center')
        table.add_row('iMessage Logs', f"{len(self.iMessage_logs)}", str(self.identified_imessage_log_count()))
        table.add_row('Emails', f"{len(self.emails)}", str(len([e for e in self.emails if e.author and e.author != UNKNOWN])))
        table.add_row('Other', f"{len(self.other_files)}", 'n/a')
        console.print('\n', Align.center(table), '\n\n')

    def sorted_imessage_logs(self) -> list[MessengerLog]:
        return sorted(self.iMessage_logs, key=lambda f: f.timestamp)

    @staticmethod
    def sort_emails(emails: list[Email]) -> list[Email]:
        return sorted(emails, key=lambda e: (e.sort_time()))


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
