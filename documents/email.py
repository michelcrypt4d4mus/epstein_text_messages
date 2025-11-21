import re
from dataclasses import dataclass, field
from datetime import datetime

from dateutil.parser import parse
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from documents.document import CommunicationDocument
from documents.email_header import AUTHOR, EMAIL_SIMPLE_HEADER_REGEX, EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX, TO_FIELDS, EmailHeader
from util.constants import *
from util.rich import *

TIME_REGEX = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}|Thursday|Monday|Tuesday|Wednesday|Friday|Saturday|Sunday).*')
DATE_REGEX = re.compile(r'(?:Date|Sent):? +(?!by|from|to|via)([^\n]{6,})\n')
EMAIL_REGEX = re.compile(r'From: (.*)')
EMAIL_HEADER_REGEX = re.compile(r'^(((Date|Subject):.*\n)*From:.*\n((Date|Sent|To|CC|Importance|Subject|Attachments):.*\n)+)')
DETECT_EMAIL_REGEX = re.compile('^(From:|.*\nFrom:|.*\n.*\nFrom:)')
BAD_EMAILER_REGEX = re.compile(r'^>|ok|re:|fwd:|((sent|attachments|subject|importance).*|.*(11111111|january|201\d|hysterical|image0|so that people|article 1.?|momminnemummin|your state|undisclosed|www\.theguardian|talk in|it was a|what do|cc:|call (back|me)).*)$', re.IGNORECASE)
EMPTY_HEADER_REGEX = re.compile(r'^\s*From:\s*\n((Date|Sent|To|CC|Importance|Subject|Attachments):\s*\n)+')
REPLY_REGEX = re.compile(r'(On ([A-Z][a-z]{2,9},)?\s*?[A-Z][a-z]{2,9}\s*\d+,\s*\d{4},?\s*(at\s*\d+:\d+\s*(AM|PM))?,?.*wrote:|-+(Forwarded|Original)\s*Message-*|Begin forwarded message:?)', re.IGNORECASE)
NOT_REDACTED_EMAILER_REGEX = re.compile(r'saved by internet', re.IGNORECASE)
CLIPPED_SIGNATURE_REPLACEMENT = '[dim]<...snipped epstein legal signature...>[/dim]'
BAD_FIRST_LINES = ['026652', '029835', '031189']
MAX_CHARS_TO_PRINT = 5000
VALID_HEADER_LINES = 14
EMAIL_INDENT = 3


@dataclass
class Email(CommunicationDocument):
    author_lowercase: str | None = field(init=False)
    header: EmailHeader = field(init=False)
    recipients: list[str | None] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._repair()
        self._extract_header()

        if self.file_id in KNOWN_EMAIL_AUTHORS:
            self.author = KNOWN_EMAIL_AUTHORS[self.file_id]
        elif not self.header.author:
            self.author = None
        else:
            self.author = _get_name(self.header.author)

        if self.file_id in KNOWN_EMAIL_RECIPIENTS:
            self.recipients = [KNOWN_EMAIL_RECIPIENTS[self.file_id]]
        else:
            self.recipients = [_get_name(r) for r in self.header.to] if self.header.to else []

        if self.header.cc or self.header.bcc:
            all_cced = (self.header.cc or []) + (self.header.bcc or [])
            cced = [_get_name(cc) for cc in all_cced]
            self.recipients += cced
            logger.debug(f"Added CC / BCC: {cced}")

        self.recipients_lower = [r.lower() if r else None for r in self.recipients]
        recipient = UNKNOWN if len(self.recipients) == 0 else (self.recipients[0] or UNKNOWN)
        self.recipient_txt = Text(recipient, COUNTERPARTY_COLORS.get(recipient, DEFAULT))
        self.timestamp = self._extract_sent_at()
        self.author_lowercase = self.author.lower() if self.author else None
        self.author_style = COUNTERPARTY_COLORS.get(self.author or UNKNOWN, DEFAULT)
        self.author_txt = Text(self.author or UNKNOWN, style=self.author_style)
        self.archive_link = archive_link(self.filename, self.author_style)

    def cleanup_email_txt(self) -> str:
        # add newline after header if header looks valid
        if not EMPTY_HEADER_REGEX.search(self.text):
            prettified_text = EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX.sub(r'\n\n\1\n', self.text).strip()
        else:
            prettified_text = self.text

        prettified_text = '\n'.join([line for line in prettified_text.split('\n') if not re.match(r'^\d{1,2}$', line)]) # Remove single digit lines
        prettified_text = escape(REPLY_REGEX.sub(r'\n\1', prettified_text))  # Newlines between quoted replies
        prettified_text = EPSTEIN_SIGNATURE.sub(CLIPPED_SIGNATURE_REPLACEMENT, prettified_text)
        return EPSTEIN_OLD_SIGNATURE.sub(CLIPPED_SIGNATURE_REPLACEMENT, prettified_text)

    def sort_time(self) -> datetime:
        timestamp = self.timestamp or parse("1/1/2001 12:01:01 AM")
        return timestamp.replace(tzinfo=None) if timestamp.tzinfo is not None else timestamp

    def _extract_sent_at(self) -> datetime | None:
        searchable_lines = self.text.split('\n')[0:VALID_HEADER_LINES]
        searchable_text = '\n'.join(searchable_lines)
        date_match = DATE_REGEX.search(searchable_text)

        if date_match:
            return _parse_timestamp(date_match.group(1).strip().replace(' (UTC)', ''))

        logger.debug(f"Failed to find timestamp, using fallback of parsing {VALID_HEADER_LINES} lines...")

        for line in searchable_lines:
            timestamp = _parse_timestamp(line.strip())

            if timestamp:
                logger.info(f"Fell back to timestamp {timestamp} in line '{line}'...")
                return timestamp

        self.log_top_lines(msg="No valid timestamp found in email")

    def _extract_header(self) -> EmailHeader | None:
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

                    value = self.lines[row_number_to_check]

                    if field_name == AUTHOR:
                        if TIME_REGEX.match(value) or value == 'Darren,':
                            logger.debug(f"Looks like a mismatch, decrementing num_headers and skipping...")
                            num_headers -= 1
                            continue
                        elif value.startswith('call me'):
                            logger.debug(f"Looks like a mismatch, Trying the next line...")
                            num_headers += 1
                            value = self.lines[i + num_headers]
                    elif field_name in TO_FIELDS:
                        if TIME_REGEX.match(value):
                            logger.debug(f"Looks like a mismatch for '{field_name}', trying next line...")
                            num_headers += 1
                            value = self.lines[i + num_headers]

                        value = [v.strip() for v in value.split(';')]

                    setattr(self.header, field_name, value)

                logger.debug(f"Corrected empty header to:\n{self.header}\n\nTop rows of file\n\n{self.top_lines(num_headers * 2)}")
            else:
                logger.debug(f"Parsed email header to:\n{self.header}")
        else:
            logger.warning(f"No header match found! Top lines:\n\n{self.top_lines()}")
            self.header = EmailHeader(field_names=[])

    def _repair(self) -> None:
        """Repair particularly janky files."""
        if self.lines[0].startswith('Grant_Smith066474"eMailContent.htm') or self.file_id in BAD_FIRST_LINES:
            self.lines = self.lines[1:]
            self.text = '\n'.join(self.lines)
        elif self.file_id == '029977':
            self.text = self.text.replace('Sent 9/28/2012 2:41:02 PM', 'Sent: 9/28/2012 2:41:02 PM')
            self.lines = self.text.split('\n')
        elif self.file_id == '031442':
            self.lines = [self.lines[0] + self.lines[1]] + self.lines[2:]
            self.text = '\n'.join(self.lines)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Panel(self.archive_link, expand=False)
        info_line = Text("Official OCR text of email from ").append(self.author_txt).append(f' to ').append(self.recipient_txt)
        info_line.append(f" probably sent at ").append(f"{self.timestamp or '?'}", style='spring_green3')
        yield Padding(info_line, (0, 0, 0, EMAIL_INDENT))
        text = self.cleanup_email_txt()

        if len(text) > MAX_CHARS_TO_PRINT:
            text = text[0:MAX_CHARS_TO_PRINT]
            text += f"\n\n[dim]<...truncated to {MAX_CHARS_TO_PRINT} characters, read the rest: {self.archive_link}...>[/dim]"

        yield Padding(Panel(text, expand=False), (0, 0, 2, EMAIL_INDENT))


def _parse_timestamp(timestamp_str: str) -> None | datetime:
    try:
        timestamp = parse(timestamp_str)
        logger.debug(f'Parsed timestamp "{timestamp}" from string "{timestamp_str}"')
        return timestamp
    except Exception as e:
        logger.debug(f'Failed to parse "{timestamp_str}" to timestamp!')


def _get_name(author: str) -> str | None:
    author = EmailHeader.cleanup_str(author)

    for name, regex in EMAILER_REGEXES.items():
        if regex.search(author):
            author = name
            break

    if BAD_EMAILER_REGEX.match(author) or TIME_REGEX.match(author):
        logger.warning(f"Name '{author}' is invalid, returning None...")
        return None

    if ', ' in author:
        names = author.split(', ')
        author = f"{names[1]} {names[0]}"

    return author
