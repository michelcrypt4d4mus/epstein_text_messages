import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from dateutil.parser import parse
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markup import escape
from rich.panel import Panel
from rich.padding import Padding
from rich.text import Text
from util.rich import ARIANE_DE_ROTHSCHILD

from .email_header import AUTHOR, EMAIL_SIMPLE_HEADER_REGEX, EmailHeader
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
REPLY_REGEX = re.compile(r'(On ([A-Z][a-z]{2,9},)?\s*?[A-Z][a-z]{2,9}\s*\d+,\s*\d{4},?\s*(at\s*\d+:\d+\s*(AM|PM))?,?.*wrote:|-+(Forwarded|Original)\s*Message-+|Begin forwarded message:?)')
NOT_REDACTED_EMAILER_REGEX = re.compile(r'saved by internet', re.IGNORECASE)
VALID_HEADER_LINES = 14
EMAIL_INDENT = 3
# iMessage
MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
MSG_DATE_FORMAT = "%m/%d/%y %I:%M:%S %p"
BAD_FIRST_LINES = ['026652', '029835', '031189']

# If found as substring consider them the author
EMAILERS = [
    'Anne Boyles',
    AL_SECKEL,
    'Bill Gates',
    'Bill Siegel',
    'Daniel Sabba',
    'Glenn Dubin',
    'Jessica Cadwell',
    JOHN_PAGE,
    'Jokeland',
    'Jes Staley',
    'Kathleen Ruderman',
    'Kenneth E. Mapp',
    'Joscha Bach',
    'Lesley Groff',
    'middle.east.update@hotmail.com',
    JONATHAN_FARKAS,
    'Mark L. Epstein',
    'nancy cain',
    'nancy portland',
    'Peggy Siegal',
    'Peter Aldhous',
    'Peter Green',
    'Robert Trivers',
    'Sample, Elizabeth',
    'Steven Victor MD',
    'The Duke',
    'Tom Barrack'
    'Weingarten, Reid',
]

EMAILER_REGEXES = {
    'Amanda Ens': re.compile(r'ens, amand', re.IGNORECASE),
    'Alan Dershowitz': re.compile(r'alan.*dershowitz', re.IGNORECASE),
    BARBRO_EHNBOM: re.compile(r'behnbom@aol.com|Barbro\s.*Ehnbom', re.IGNORECASE),
    'Barry J. Cohen': re.compile(r'barry (j.? )?cohen?', re.IGNORECASE),
    'Boris Nikolic': re.compile(r'boris nikoli', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterpris', re.IGNORECASE),
    DARREN_INDKE: re.compile(r'^darren$|darren [il]ndyke|dkiesq', re.IGNORECASE),
    'David Stern': re.compile(r'David Stern?', re.IGNORECASE),
    EDWARD_EPSTEIN: re.compile(r'Edward (Jay )?Epstein', re.IGNORECASE),
    EHUD_BARAK: re.compile(r'(ehud|h)\s*barak', re.IGNORECASE),
    'Faith Kates': re.compile(r'faith kate', re.IGNORECASE),
    GHISLAINE_MAXWELL: re.compile(r'g ?max(well)?', re.IGNORECASE),
    'Google Alerts': re.compile(r'google\s?alerts', re.IGNORECASE),
    'Intelligence Squared': re.compile(r'intelligence\s*squared', re.IGNORECASE),
    'jackie perczel':  re.compile(r'jackie percze', re.IGNORECASE),
    'Jabor Y.': re.compile(r'^[ji]abor\s*y', re.IGNORECASE),
    JEFFREY_EPSTEIN: re.compile(r'[djl]ee[vy]acation[©@]|jeffrey E\.|Jeffrey Epstein', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|joichi|^joi$', re.IGNORECASE),
    JOHNNY_EL_HACHEM: re.compile('el hachem johnny|johnny el hachem', re.IGNORECASE),
    'Kathy Ruemmler': re.compile(r'Kathy Ruemmle', re.IGNORECASE),
    'Ken Starr': re.compile('starr, ken', re.IGNORECASE),
    LANDON_THOMAS: re.compile('landon thomas|thomas jr.?, landon', re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r'La(wrence|rry).*Summer|^LH$|^LHS', re.IGNORECASE),
    LEON_BLACK: re.compile(r'Leon Blac', re.IGNORECASE),
    'lilly sanchez': re.compile(r'Lilly.*Sanchez', re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r'Lawrence Kraus', re.IGNORECASE),
    'Lisa New': re.compile(r'Lisa New?$', re.IGNORECASE),
    'Mohamed Waheed Hassan': re.compile(r'Mohamed Waheed', re.IGNORECASE),
    'Martin Weinberg': re.compile(r'martin.*?weinberg', re.IGNORECASE),
    'Michael Wolff': re.compile(r'Michael\s*Wol(ff|i)', re.IGNORECASE),
    'Nicholas Ribis': re.compile(r'Nicholas Rib', re.IGNORECASE),
    'Paul Krassner': re.compile(r'Pa\s?ul Krassner', re.IGNORECASE),
    'Paul Morris': re.compile(r'morris, paul|Paul Morris', re.IGNORECASE),
    'Richard Kahn': re.compile(r'rich(ard)? kahn?', re.IGNORECASE),
    'Robert Lawrence Kuhn': re.compile(r'Robert\s*(Lawrence)?\s*Kuhn', re.IGNORECASE),
    'Scott J. Link': re.compile(r'scott j. lin', re.IGNORECASE),
    'Sean Bannon': re.compile(r'sean banno', re.IGNORECASE),
    SOON_YI: re.compile(r'Soon[- ]Yi Previn?', re.IGNORECASE),
    'Stephen Hanson': re.compile(r'ste(phen|ve) hanson|Shanson900', re.IGNORECASE),
    STEVE_BANNON: re.compile(r'steve banno[nr]?', re.IGNORECASE),
    'Steven Sinofsky': re.compile(r'Steven Sinofsk', re.IGNORECASE),
    SULTAN_BIN_SULAYEM: re.compile(r'Sultan bin Sulay', re.IGNORECASE),
    TERRY_KAFKA: re.compile(r'Terry Kafk', re.IGNORECASE),
}

KNOWN_EMAILS = {
    '026064': ARIANE_DE_ROTHSCHILD,
    '026069': ARIANE_DE_ROTHSCHILD,
    '030741': ARIANE_DE_ROTHSCHILD,
    '026018': ARIANE_DE_ROTHSCHILD,
    '026745': BARBRO_EHNBOM,      # Signature
    '031227': 'Moskowitz, Bennet J.',
    '031442': 'Christina Galbraith',
    '026625': DARREN_INDKE,
    '026290': DAVID_SCHOEN,       # Signature
    '031339': DAVID_SCHOEN,       # Signature
    '031492': DAVID_SCHOEN,       # Signature
    '031560': DAVID_SCHOEN,       # Signature
    '026287': DAVID_SCHOEN,       # Signature
    '031460': EDWARD_EPSTEIN,
    '026547': 'Gerald G. Barton',
    '031120': GWENDOLYN_BECK,        # Signature
    '029968': GWENDOLYN_BECK,        # Signature
    '029970': GWENDOLYN_BECK,
    '029960': GWENDOLYN_BECK,     # Reply
    '026024': 'Jean Huguen',
    '026024': 'Jean Huguen',  # Signature
    '030997': JEFFREY_EPSTEIN,
    '029779': JEFFREY_EPSTEIN,
    '022949': JEFFREY_EPSTEIN,
    '028770': JEFFREY_EPSTEIN,
    '029692': JEFFREY_EPSTEIN,
    '031624': JEFFREY_EPSTEIN,
    '030768': JEFFREY_EPSTEIN,
    '016692': JOHN_PAGE,
    '016693': JOHN_PAGE,
    '028507': JONATHAN_FARKAS,
    '031732': JONATHAN_FARKAS,
    '026764': 'Barry J. Cohen',
    '030478': LANDON_THOMAS,
    '029013': LARRY_SUMMERS,
    '031129': LARRY_SUMMERS,
    '029196': LAWRENCE_KRAUSS,
    '028789': LAWRANCE_VISOSKI,
    '027046': LAWRANCE_VISOSKI,
    '030472': "Martin Weinberg",   #Maybe. in reply
    '030235': MELANIE_WALKER,    # In fwd
    '022193': NADIA_MARCINKO,
    '021814': NADIA_MARCINKO,
    '021808': NADIA_MARCINKO,
    '022190': NADIA_MARCINKO,
    '021811': NADIA_MARCINKO,      # Signature and email address in the message
    '029981': 'Paula',        # reply
    '031694': 'Peggy Siegal',
    '029020': 'Renata Bolotova',   # Signature
    '029003': SOON_YI,
    '029005': SOON_YI,
    '029007': SOON_YI,
    '029010': SOON_YI,
    '026620': TERRY_KAFKA,
    '028482': TERRY_KAFKA,    # Signature
    '029992': TERRY_KAFKA,    # Reply
    # '026571': '(unknown french speaker)',
    '017581': 'Lisa Randall',
}

for emailer in EMAILERS:
    if emailer in EMAILER_REGEXES:
        raise RuntimeError(f"Can't overwrite emailer regex for '{emailer}'")

    EMAILER_REGEXES[emailer] = re.compile(emailer, re.IGNORECASE)

EPSTEIN_SIGNATURE = re.compile(
r"""please note
The information contained in this communication is
confidential, may be attorney-client privileged, may
constitute inside information, and is intended only for
the use of the addressee. It is the property of
JEE
Unauthorized use, disclosure or copying of this
communication or any part thereof is strictly prohibited
and may be unlawful. If you have received this
communication in error, please notify us immediately by(\n\d\s*)?
return e-mail or by e-mail to jeevacation.*gmail.com, and
destroy this communication and all copies thereof,
including all attachments. copyright -all rights reserved"""
)


@dataclass
class Document:
    file_path: Path
    filename: str = field(init=False)
    text: str = field(init=False)
    file_id: str = field(init=False)
    file_lines: list[str] = field(init=False)
    num_lines: int = field(init=False)
    length: int = field(init=False)

    def __post_init__(self):
        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)
        self.text = load_file(self.file_path)
        self.length = len(self.text)
        self.file_lines = self.text.split('\n')
        self.num_lines = len(self.file_lines)

    def top_lines(self, n: int = 10) -> str:
        return '\n'.join(self.file_lines[0:n])

    def log_top_lines(self, n: int = 10, msg: str | None = None) -> None:
        logger.info(f"{msg + '. ' if msg else ''}Top lines of '{self.filename}':\n\n{self.top_lines(n)}")


@dataclass
class CommunicationDocument(Document):
    author: str | None = field(init=False)
    author_style: str = field(init=False)
    author_txt: Text = field(init=False)
    timestamp: datetime | None = field(init=False)

    def __post_init__(self):
        super().__post_init__()


@dataclass
class MessengerLog(CommunicationDocument):
    author_str: str = field(init=False)
    hint_txt: Text | None = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.author = KNOWN_COUNTERPARTY_FILE_IDS.get(self.file_id, GUESSED_COUNTERPARTY_FILE_IDS.get(self.file_id))
        self.author_str = self.author or UNKNOWN
        self.author_style = COUNTERPARTY_COLORS.get(self.author_str, DEFAULT)
        self.author_txt = Text(self.author_str, style=self.author_style)

        if self.file_id in KNOWN_COUNTERPARTY_FILE_IDS:
            self.hint_txt = Text(f" Found confirmed counterparty ", style='grey').append(self.author_txt).append(f" for file ID {self.file_id}.")
        elif self.file_id in GUESSED_COUNTERPARTY_FILE_IDS:
            self.author_str += ' (?)'
            self.author_txt = Text(self.author_str, style=self.author_style)
            self.hint_txt = Text(" (This is probably a conversation with ", style='grey').append(self.author_txt).append(')')
        else:
            self.hint_txt = None

        # Get timestamp
        for match in MSG_REGEX.finditer(self.text):
            timestamp_str = match.group(2).strip()

            try:
                self.timestamp = datetime.strptime(timestamp_str, MSG_DATE_FORMAT)
                break
            except ValueError as e:
                logger.debug(f"[WARNING] Failed to parse '{timestamp_str}' to datetime! Using next match. Error: {e}'")


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

        self.recipients = [_get_name(r) for r in self.header.to] if self.header.to else []
        self.recipients_lower = [r.lower() if r else None for r in self.recipients]
        self.timestamp = self.extract_sent_at()
        self.author_lowercase = self.author.lower() if self.author else None
        self.author_style = COUNTERPARTY_COLORS.get(self.author or UNKNOWN, DEFAULT)
        self.author_txt = Text(self.author or UNKNOWN, style=self.author_style)

    def cleanup_email_txt(self) -> str:
        # add newline after header if header looks valid
        if not EMPTY_HEADER_REGEX.search(self.text):
            prettified_text = EMAIL_HEADER_REGEX.sub(r'\1\n', self.text, 1)
        else:
            prettified_text = self.text

        prettified_text = REPLY_REGEX.sub(r'\n\1', prettified_text)  # Insert newlines between quoted replies
        return EPSTEIN_SIGNATURE.sub('<...clipped epstein legal signature...>', prettified_text)

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

                    if field_name == AUTHOR and (TIME_REGEX.match(value) or value == 'Darren,'):
                        logger.debug(f"Looks like a mismatch, decrementing num_headers and skipping!")
                        num_headers -= 1
                        continue

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
        info_line = Text(" Email from ").append(self.author_txt)
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
                        self.email_recipient_counts[recipient.lower()] += 1

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
            console.print('\n\n', Panel(Text(f"{len(emails)} emails to/from {author} Found)", justify='center')), '\n', style='bold reverse')
        else:
            logger.warning(f"No emails found for {author}")

        for email in emails:
            console.print(email)

    def sorted_imessage_logs(self) -> list[MessengerLog]:
        return sorted(self.iMessage_logs, key=lambda f: f.timestamp)

    def emails_for(self, author: str | None) -> list[Email]:
        author = author.lower() if author else None
        emails_by = [e for e in self.emails if e.author_lowercase == author]
        emails_to = [e for e in self.emails if author in e.recipients]
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
