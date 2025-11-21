import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from dateutil.parser import parse
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.text import Text

from .constants import *
from .documents.document import CommunicationDocument, Document
from .documents.messenger_log import MSG_REGEX, MessengerLog
from .email_header import AUTHOR, EMAIL_SIMPLE_HEADER_REGEX, EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX, EmailHeader
from .env import deep_debug, is_debug
from .file_helper import extract_file_id, load_file, move_json_file
from .rich import *

TIME_REGEX = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}|Thursday|Monday|Tuesday|Wednesday|Friday|Saturday|Sunday).*')
DATE_REGEX = re.compile(r'(?:Date|Sent):? +(?!by|from|to|via)([^\n]{6,})\n')
EMAIL_REGEX = re.compile(r'From: (.*)')
EMAIL_HEADER_REGEX = re.compile(r'^(((Date|Subject):.*\n)*From:.*\n((Date|Sent|To|CC|Importance|Subject|Attachments):.*\n)+)')
DETECT_EMAIL_REGEX = re.compile('^(From:|.*\nFrom:|.*\n.*\nFrom:)')
BAD_EMAILER_REGEX = re.compile(r'^>|ok|re:|fwd:|((sent|attachments|subject|importance).*|.*(11111111|january|201\d|hysterical|image0|so that people|article 1.?|momminnemummin|your state|undisclosed|www\.theguardian|talk in|it was a|what do|cc:|call (back|me)).*)$', re.IGNORECASE)
EMPTY_HEADER_REGEX = re.compile(r'^\s*From:\s*\n((Date|Sent|To|CC|Importance|Subject|Attachments):\s*\n)+')
REPLY_REGEX = re.compile(r'(On ([A-Z][a-z]{2,9},)?\s*?[A-Z][a-z]{2,9}\s*\d+,\s*\d{4},?\s*(at\s*\d+:\d+\s*(AM|PM))?,?.*wrote:|-+(Forwarded|Original)\s*Message-+|Begin forwarded message:?)', re.IGNORECASE)
NOT_REDACTED_EMAILER_REGEX = re.compile(r'saved by internet', re.IGNORECASE)
VALID_HEADER_LINES = 14
EMAIL_INDENT = 3
CLIPPED_SIGNATURE_REPLACEMENT = '<...clipped epstein legal signature...>'
BAD_FIRST_LINES = ['026652', '029835', '031189']


@dataclass
class Email(CommunicationDocument):
    author_lowercase: str | None = field(init=False)
    header: EmailHeader = field(init=False)
    recipients: list[str | None] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._repair()
        self.extract_header()

        if self.file_id in KNOWN_EMAILS:
            self.author = KNOWN_EMAILS[self.file_id]
        elif not self.header.author:
            self.author = None
        else:
            self.author = _get_name(self.header.author)

        if self.file_id in KNOWN_RECIPIENTS:
            self.recipients = [KNOWN_RECIPIENTS[self.file_id]]
        else:
            self.recipients = [_get_name(r) for r in self.header.to] if self.header.to else []

        self.recipients_lower = [r.lower() if r else None for r in self.recipients]
        recipient = UNKNOWN if len(self.recipients) == 0 else (self.recipients[0] or UNKNOWN)
        self.recipient_txt = Text(recipient, COUNTERPARTY_COLORS.get(recipient, DEFAULT))
        self.timestamp = self.extract_sent_at()
        self.author_lowercase = self.author.lower() if self.author else None
        self.author_style = COUNTERPARTY_COLORS.get(self.author or UNKNOWN, DEFAULT)
        self.author_txt = Text(self.author or UNKNOWN, style=self.author_style)

    def cleanup_email_txt(self) -> str:
        # add newline after header if header looks valid
        if not EMPTY_HEADER_REGEX.search(self.text):
            prettified_text = EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX.sub(r'\n\n\1\n', self.text).strip()
        else:
            prettified_text = self.text

        prettified_text = REPLY_REGEX.sub(r'\n\1', prettified_text)  # Insert newlines between quoted replies
        prettified_text = EPSTEIN_SIGNATURE.sub(CLIPPED_SIGNATURE_REPLACEMENT, prettified_text)
        return EPSTEIN_OLD_SIGNATURE.sub(CLIPPED_SIGNATURE_REPLACEMENT, prettified_text)

    def extract_sent_at(self) -> datetime | None:
        searchable_lines = self.text.split('\n')[0:VALID_HEADER_LINES]
        searchable_text = '\n'.join(searchable_lines)
        date_match = DATE_REGEX.search(searchable_text)

        if not date_match:
            logger.debug(f"Failed to find timestamp, using fallback of parsing top {VALID_HEADER_LINES} lines...")

            for line in searchable_lines:
                timestamp = parse_timestamp(line.strip())

                if timestamp:
                    logger.info(f"Fell back to timestamp {timestamp} in line '{line}'...")
                    return timestamp

            self.log_top_lines(msg="No valid timestamp found in email")
            return

        return parse_timestamp(date_match.group(1).strip().replace(' (UTC)', ''))

    def extract_header(self) -> EmailHeader | None:
        header_match = EMAIL_SIMPLE_HEADER_REGEX.search(self.text)

        if header_match:
            self.header = EmailHeader.from_str(header_match.group(0))

            # Sometimes the headers and values are on separate rows
            if self.header.is_empty():
                num_headers = len(self.header.field_names)

                for i, field_name in enumerate(self.header.field_names):
                    row_number_to_check = i + num_headers

                    if row_number_to_check > (self.num_lines - 1):
                        logger.warning(f"Ran out of rows to check for a value for '{field_name}'")
                        break

                    value = self.file_lines[row_number_to_check]

                    if field_name == AUTHOR:
                        if TIME_REGEX.match(value) or value == 'Darren,':
                            logger.debug(f"Looks like a mismatch, decrementing num_headers and skipping...")
                            num_headers -= 1
                            continue
                        elif value.startswith('call me'):
                            logger.debug(f"Looks like a mismatch, Trying the next line...")
                            num_headers += 1
                            value = self.file_lines[i + num_headers]

                    setattr(self.header, field_name, [v.strip() for v in value.split(';')] if field_name == 'to' else value)

                logger.debug(f"Corrected empty header to:\n{self.header}\n\nTop rows of file\n\n{self.top_lines(num_headers * 2)}")
            else:
                logger.debug(f"Parsed email header to:\n{self.header}")
        else:
            logger.warning(f"No header match found! Top lines:\n\n{self.top_lines()}")
            self.header = EmailHeader(field_names=[])

    def sort_time(self) -> datetime:
        timestamp = self.timestamp or parse("1/1/2001 12:01:01 AM")
        return timestamp.replace(tzinfo=None) if timestamp.tzinfo is not None else timestamp

    def _repair(self) -> None:
        """Repair particularly janky files."""
        if self.file_lines[0].startswith('Grant_Smith066474"eMailContent.htm') or self.file_id in BAD_FIRST_LINES:
            self.file_lines = self.file_lines[1:]
            self.text = '\n'.join(self.file_lines)
        elif self.file_id == '029977':
            self.text = self.text.replace('Sent 9/28/2012 2:41:02 PM', 'Sent: 9/28/2012 2:41:02 PM')
            self.file_lines = self.text.split('\n')
        elif self.file_id == '031442':
            self.file_lines = [self.file_lines[0] + self.file_lines[1]] + self.file_lines[2:]
            self.text = '\n'.join(self.file_lines)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Panel(archive_link(self.filename, self.author_style), expand=False)
        info_line = Text(" Email from ").append(self.author_txt).append(f' to ').append(self.recipient_txt)
        info_line.append(f" probably sent at ").append(f"{self.timestamp or '?'}", style='spring_green3')
        yield Padding(info_line, (0, 0, 0, EMAIL_INDENT))
        email_panel = Panel(escape(self.cleanup_email_txt()), expand=False)
        yield Padding(email_panel, (0, 0, 2, EMAIL_INDENT))


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

                    print_top_lines(document.text)

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


def parse_timestamp(timestamp_str: str) -> None | datetime:
    try:
        timestamp = parse(timestamp_str)
        logger.debug(f'Parsed timestamp "{timestamp}" from string "{timestamp_str}"')
        return timestamp
    except Exception as e:
        logger.debug(f'Failed to parse "{timestamp_str}" to timestamp!')


valid_emailer = lambda emailer: not BAD_EMAILER_REGEX.match(emailer)


def _get_name(author: str) -> str | None:
    author = EmailHeader.cleanup_str(author)

    for name, regex in EMAILER_REGEXES.items():
        if regex.search(author):
            author = name
            break

    if not valid_emailer(author) or TIME_REGEX.match(author):
        logger.warning(f"Name '{author}' is invalid, returning None...")
        return None

    if ', ' in author:
        names = author.split(', ')
        author = f"{names[1]} {names[0]}"

    return author
