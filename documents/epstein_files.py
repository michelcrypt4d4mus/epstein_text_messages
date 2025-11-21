from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.text import Text

from util.constants import *
from util.documents.document import Document
from util.documents.messenger_log import MSG_REGEX, MessengerLog
from util.env import deep_debug, is_debug
from util.file_helper import move_json_file
from util.rich import console, logger
from util.emails import DETECT_EMAIL_REGEX, Email


@dataclass
class EpsteinFiles:
    all_files: list[Path]
    emails: list[Email] = field(init=False)
    iMessage_logs: list[MessengerLog] = field(init=False)
    other_files: list[Document] = field(init=False)
    emailer_counts: dict[str, int] = field(init=False)
    email_recipient_counts: dict[str, int] = field(init=False)

    def __post_init__(self):
        self.emails = []
        self.iMessage_logs = []
        self.other_files = []
        self.emailer_counts = defaultdict(int)
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
            else:
                emailer = None

                if DETECT_EMAIL_REGEX.match(document.text):  # Handle emails
                    logger.info('Email...')
                    email = Email(file_arg)
                    self.emails.append(email)
                    emailer = email.author or UNKNOWN
                    self.emailer_counts[emailer.lower()] += 1
                    logger.debug(f"Emailer: '{emailer}'")

                    for recipient in email.recipients:
                        self.email_recipient_counts[recipient.lower() if recipient else UNKNOWN] += 1

                    if len(emailer) >= 3 and emailer != UNKNOWN:
                        continue  # Don't proceed to printing debug contents if we found a valid email
                else:
                    logger.info('Unknown file type...')
                    self.other_files.append(document)

                if is_debug:
                    if emailer and emailer == UNKNOWN:
                        console.print(f"   -> Redacted email '{file_arg.name}' with {document.num_lines} lines. First lines:")
                    elif emailer and emailer != UNKNOWN:
                        console.print(f"   -> Failed to find valid email for '{file_arg.name}' (got '{emailer}')", style='red')
                    else:
                        console.print(f"   -> Unknown kind of file '{file_arg.name}' with {document.num_lines} lines. First lines:", style='dim')

                    document.log_top_lines()

                continue

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
        emails_to = []
        emails_by = [e for e in self.emails if e.author_lowercase == author]

        if author is None:
            emails_to = [e for e in self.emails if e.author == JEFFREY_EPSTEIN and (None in e.recipients or len(e.recipients) == 0)]
        else:
            emails_to = [e for e in self.emails if author in e.recipients_lower]

        return EpsteinFiles.sort_emails(emails_by + emails_to)

    @classmethod
    def sort_emails(cls, emails: list[Email]) -> list[Email]:
        return sorted(emails, key=lambda e: (e.sort_time()))
