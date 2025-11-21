from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from documents.document import Document
from documents.email import DETECT_EMAIL_REGEX, Email
from documents.messenger_log import MSG_REGEX, MessengerLog
from util.constants import *
from util.env import deep_debug, is_debug
from util.file_helper import DOCS_DIR, move_json_file
from util.rich import console, logger


@dataclass
class EpsteinFiles:
    all_files: list[Path] = field(init=False)
    emails: list[Email] = field(init=False)
    iMessage_logs: list[MessengerLog] = field(init=False)
    other_files: list[Document] = field(init=False)
    email_author_counts: dict[str, int] = field(init=False)
    email_recipient_counts: dict[str, int] = field(init=False)

    def __post_init__(self):
        self.all_files = [f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]
        self.emails = []
        self.iMessage_logs = []
        self.other_files = []
        self.email_author_counts = defaultdict(int)
        self.email_recipient_counts = defaultdict(int)

        for file_arg in self.all_files:
            if is_debug:
                console.print(f"\nScanning '{file_arg.name}'...")

            document = Document(file_arg)

            if document.length == 0:
                logger.info('Skipping empty file...')
                continue
            elif document.text[0] == '{':  # Check for JSON
                move_json_file(file_arg)
            elif MSG_REGEX.search(document.text):
                logger.info('iMessage log file...')
                self.iMessage_logs.append(MessengerLog(file_arg))
            elif DETECT_EMAIL_REGEX.match(document.text):  # Handle emails
                email = Email(file_arg)
                self.emails.append(email)
                author = email.author or UNKNOWN
                self.email_author_counts[author.lower()] += 1
                logger.info(f"Email (author='{author}')")

                for recipient in email.recipients:
                    self.email_recipient_counts[recipient.lower() if recipient else UNKNOWN] += 1

                if len(author) <= 3 or author == UNKNOWN:
                    email.log_top_lines(msg=f"Redacted or invalid email author '{author}'")
            else:
                logger.info('Unknown file type...')
                self.other_files.append(document)
                document.log_top_lines()

    def print_emails_for(self, author: str | None) -> None:
        emails = self.emails_for(author)
        author = author or '[redacted]'

        if len(emails) > 0:
            console.print('\n\n', Panel(Text(f"Found {len(emails)} emails to/from {author}", justify='center')), '\n', style='bold reverse')
        else:
            logger.warning(f"No emails found for {author}")

        for email in emails:
            console.print(email)

    def sorted_imessage_logs(self) -> list[MessengerLog]:
        return sorted(self.iMessage_logs, key=lambda f: f.timestamp)

    def emails_for(self, author: str | None) -> list[Email]:
        author = author.lower() if author else None
        emails_by = [e for e in self.emails if e.author_lowercase == author]
        emails_to = []

        if author is None:
            emails_to = [
                e for e in self.emails
                if e.author == JEFFREY_EPSTEIN and (None in e.recipients or len(e.recipients) == 0)
            ]
        else:
            emails_to = [e for e in self.emails if author in e.recipients_lower]

        return EpsteinFiles.sort_emails(emails_by + emails_to)

    def identified_imessage_log_count(self) -> int:
        return len([log for log in self.iMessage_logs if log.author])

    def imessage_msg_count(self) -> int:
        return sum([log.msg_count for log in self.sorted_imessage_logs()])

    @classmethod
    def sort_emails(cls, emails: list[Email]) -> list[Email]:
        return sorted(emails, key=lambda e: (e.sort_time()))
