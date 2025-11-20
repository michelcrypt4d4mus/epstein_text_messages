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

from .env import deep_debug, is_debug
from .file_helper import extract_file_id, load_file, move_json_file
from .rich import (COUNTERPARTY_COLORS, DEFAULT, GUESSED_COUNTERPARTY_FILE_IDS, KNOWN_COUNTERPARTY_FILE_IDS,
    JOI_ITO, LARRY_SUMMERS, MAX_PREVIEW_CHARS, SOON_YI, UNKNOWN, archive_link, console, logger, print_top_lines)

DATE_REGEX = re.compile(r'(?:Date|Sent):? +(?!by|from|to|via)([^\n]{6,})\n')
EMAIL_REGEX = re.compile(r'From: (.*)')
EMAIL_HEADER_REGEX = re.compile(r'^(((Date|Subject):.*\n)*From:.*\n((Date|Sent|To|CC|Importance|Subject|Attachments):.*\n)+)')
DETECT_EMAIL_REGEX = re.compile('^(From:|.*\nFrom:|.*\n.*\nFrom:)')
BAD_EMAILER_REGEX = re.compile(r'^>|ok|((sent|attachments|subject|importance).*|.*(11111111|january|201\d|hysterical|article 1.?|momminnemummin|talk in|it was a|what do|cc:|call (back|me)).*)$', re.IGNORECASE)
EMPTY_HEADER_REGEX = re.compile(r'From:\s*\n((Date|Sent|To|CC|Importance|Subject|Attachments):\s*\n)+')
BROKEN_EMAIL_REGEX = re.compile(r'^From:\s*\nSent:\s*\nTo:\s*\n(?:(?:CC|Importance|Subject|Attachments):\s*\n)*(?!CC|Importance|Subject|Attachments)([a-zA-Z]{2,}.*|\[triyersr@gmail.com\])\n')
REPLY_REGEX = re.compile(r'(On ([A-Z][a-z]{2,9},)?\s*?[A-Z][a-z]{2,9}\s*\d+,\s*\d{4},?\s*(at\s*\d+:\d+\s*(AM|PM))?,?.*wrote:|-+Original\s*Message-+)')
NOT_REDACTED_EMAILER_REGEX = re.compile(r'saved by internet', re.IGNORECASE)
VALID_HEADER_LINES = 14
EMAIL_INDENT = 3
# iMessage
MSG_REGEX = re.compile(r'Sender:(.*?)\nTime:(.*? (AM|PM)).*?Message:(.*?)\s*?((?=(\nSender)|\Z))', re.DOTALL)
MSG_DATE_FORMAT = "%m/%d/%y %I:%M:%S %p"
# Names
AL_SECKEL = 'Al Seckel'
ARIANE_DE_ROTHSCHILD = 'Ariane de Rothschild'
BARBRO_EHNBOM = 'Barbro Ehnbom'
DARREN_INDKE = 'Darren Indke'
EDWARD_EPSTEIN = 'Edward Epstein'
EHUD_BARAK = 'Ehud Barak'
GHISLAINE_MAXWELL = 'Ghislaine Maxwell'
JEFFREY_EPSTEIN = 'Jeffrey Epstein'
JOHN_PAGE = 'John Page'
JOHNNY_EL_HACHEM = 'Johnny el Hachem'
JONATHAN_FARKAS = 'Jonathan Farkas'
LAWRENCE_KRAUSS = 'Lawrence Krauss'
LAWRANCE_VISOSKI = 'Lawrance Visoski'
NADIA_MARCINKO = 'Nadia Marcinko'
STEVE_BANNON = 'Steve Bannon'

EMAILERS = [
    AL_SECKEL,
    'Daniel Sabba',
    'Glenn Dubin',
    'Jessica Cadwell',
    JOHN_PAGE,
    'Jokeland',
    'Kathleen Ruderman',
    'Lesley Groff',
    'Michael Wolff',
    JONATHAN_FARKAS,
    'Peggy Siegal',
    'Richard Kahn',
    'Robert Kuhn',
    'Robert Trivers',
    'Sample, Elizabeth',
    'Steven Victor MD',
    'Weingarten, Reid',
]

EMAILER_REGEXES = {
    'Amanda Ens': re.compile(r'ens, amand', re.IGNORECASE),
    BARBRO_EHNBOM: re.compile(r'behnbom@aol.com|Barbro\s.*Ehnbom', re.IGNORECASE),
    'Barry J. Cohen': re.compile(r'barry (j.? )?cohen?', re.IGNORECASE),
    'Boris Nikolic': re.compile(r'boris nikoli', re.IGNORECASE),
    'Dangene and Jennie Enterprise': re.compile(r'Dangene and Jennie Enterpris', re.IGNORECASE),
    DARREN_INDKE: re.compile(r'^darren$|darren [il]ndyke', re.IGNORECASE),
    'David Stern': re.compile(r'David Stern?', re.IGNORECASE),
    EDWARD_EPSTEIN: re.compile(r'Edward (Jay )?Epstein', re.IGNORECASE),
    EHUD_BARAK: re.compile(r'(ehud|h)\s*barak', re.IGNORECASE),
    GHISLAINE_MAXWELL: re.compile(r'g ?max(well)?', re.IGNORECASE),
    'Google Alerts': re.compile(r'google\s?alerts', re.IGNORECASE),
    JEFFREY_EPSTEIN: re.compile(r'jee[vy]acation[©@]|jeffrey E\.|Jeffrey Epstein', re.IGNORECASE),
    JOI_ITO: re.compile(r'ji@media.mit.?edu|joichi|^joi$', re.IGNORECASE),
    JOHNNY_EL_HACHEM: re.compile('el hachem johnny|johnny el hachem', re.IGNORECASE),
    'Kathy Ruemmler': re.compile(r'Kathy Ruemmle', re.IGNORECASE),
    'Ken Starr': re.compile('starr, ken', re.IGNORECASE),
    'Landon Thomas Jr.': re.compile('landon thomas jr|thomas jr.?, landon', re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r'La(wrence|rry).*Summer|^LHS?$', re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r'Lawrence Kraus', re.IGNORECASE),
    'Lisa New': re.compile(r'Lisa New?$', re.IGNORECASE),
    'Mohamed Waheed Hassan': re.compile(r'Mohamed Waheed', re.IGNORECASE),
    'Martin Weinberg': re.compile(r'martin (g.* )weinberg', re.IGNORECASE),
    'Nicholas Ribis': re.compile(r'Nicholas Rib', re.IGNORECASE),
    'Paul Krassner': re.compile(r'Pa\s?ul Krassner', re.IGNORECASE),
    'Robert Lawrence Kuhn': re.compile(r'Robert\s*(Lawrence\s*)?Kuhn', re.IGNORECASE),
    'Scott J. Link': re.compile(r'scott j. lin', re.IGNORECASE),
    'Sean Bannon': re.compile(r'sean banno', re.IGNORECASE),
    'Stephen Hanson': re.compile(r'ste(phen|ve) hanson|Shanson900', re.IGNORECASE),
    STEVE_BANNON: re.compile(r'steve banno[nr]?', re.IGNORECASE),
}

KNOWN_EMAILS = {
    '026064': ARIANE_DE_ROTHSCHILD,
    '026069': ARIANE_DE_ROTHSCHILD,
    '030741': ARIANE_DE_ROTHSCHILD,
    '026018': ARIANE_DE_ROTHSCHILD,
    '026625': DARREN_INDKE,
    '026547': 'Gerald G. Barton',
    '031120': 'Gwendolyn',        # Signature
    '029968': 'Gwendolyn',        # Signature
    '026024': 'Jean Huguen',
    '029779': JEFFREY_EPSTEIN,
    '022949': JEFFREY_EPSTEIN,
    '028770': JEFFREY_EPSTEIN,
    '029692': JEFFREY_EPSTEIN,
    '031624': JEFFREY_EPSTEIN,
    '016692': JOHN_PAGE,
    '016693': JOHN_PAGE,
    '028507': JONATHAN_FARKAS,
    '031732': JONATHAN_FARKAS,
    '029013': LARRY_SUMMERS,
    '029196': LAWRENCE_KRAUSS,
    '028789': LAWRANCE_VISOSKI,
    '027046': LAWRANCE_VISOSKI,
    '022190': NADIA_MARCINKO,
    '029020': 'Renata Bolotova',   # Signature
    '029003': SOON_YI,
    '029005': SOON_YI,
    '029007': SOON_YI,
    '029010': SOON_YI,
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


@dataclass
class MessengerLog(Document):
    author: str = field(init=False)
    author_str: str = field(init=False)
    author_txt: Text = field(init=False)
    hint_txt: Text | None = field(init=False)
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.author = KNOWN_COUNTERPARTY_FILE_IDS.get(self.file_id, GUESSED_COUNTERPARTY_FILE_IDS.get(self.file_id)) or UNKNOWN
        self.author_str = self.author
        author_style = COUNTERPARTY_COLORS.get(self.author, DEFAULT)
        self.author_txt = Text(self.author, style=author_style)

        if self.file_id in KNOWN_COUNTERPARTY_FILE_IDS:
            self.hint_txt = Text(f" Found confirmed counterparty ", style='grey').append(self.author_txt).append(f" for file ID {self.file_id}.")
        elif self.file_id in GUESSED_COUNTERPARTY_FILE_IDS:
            self.author_str = self.author + ' (?)'
            self.author_txt = Text(self.author_str, style=author_style)
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
class Email(Document):
    author: str | None = field(init=False)
    author_lowercase: str | None = field(init=False)
    timestamp: datetime | None = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.author = self.extract_email_sender()
        self.author_lowercase = self.author.lower() if self.author else None
        self.timestamp = self.extract_sent_at()

    def extract_email_sender(self) -> str | None:
        if self.file_id in KNOWN_EMAILS:
            return KNOWN_EMAILS[self.file_id]

        email_match = EMAIL_REGEX.search(self.text)
        broken_match = BROKEN_EMAIL_REGEX.search(self.text)
        emailer = None

        if broken_match:
            emailer = broken_match.group(1)
        elif email_match:
            emailer = email_match.group(1)

        if not emailer:
            return

        emailer = emailer.strip().lstrip('"').lstrip("'").rstrip('"').rstrip("'").strip()
        emailer = emailer.strip('_').strip('[').strip(']').strip('*').strip('<').strip('•').rstrip(',').strip()

        for name, regex in EMAILER_REGEXES.items():
            if regex.search(emailer):
                emailer = name
                break

        if ' [' in emailer:
            emailer = emailer.split(' [')[0]

        if not valid_emailer(emailer):
            return
        elif emailer == 'Ed' and 'EDWARD JAY EPSTEIN' in self.text:
            return EDWARD_EPSTEIN

        return emailer

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
            logger.info(f"Failed to find timestamp, using fallback of parsing top {VALID_HEADER_LINES} lines...")

            for line in searchable_lines:
                timestamp = parse_timestamp(line.strip())

                if timestamp:
                    logger.info(f"Fell back to timestamp {timestamp} in line '{line}'...")
                    return timestamp

            top_text = '\n'.join(self.text.split("\n")[0:10])[0:MAX_PREVIEW_CHARS]
            logger.info(f"Timestamp not found in email, top lines:\n{top_text}")
            return

        timestamp_str = date_match.group(1).strip()
        timestamp_str = timestamp_str.replace(' (UTC)', '') if timestamp_str.endswith(' (UTC)') else timestamp_str
        return parse_timestamp(timestamp_str)

    def is_redacted(self) -> bool:
        return self.author is None

    def sort_time(self) -> datetime:
        timestamp = self.timestamp or parse("1/1/2001 12:01:01 AM")
        return timestamp.replace(tzinfo=None) if timestamp.tzinfo is not None else timestamp

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Panel(archive_link(self.filename), expand=False)
        email_info = f" Email from {self.author or UNKNOWN} probably sent at '{self.timestamp or '?'}'"
        yield Padding(Text(email_info, style='dim'), (0, 0, 0, EMAIL_INDENT))
        email_panel = Panel(escape(self.cleanup_email_txt()), expand=False)
        yield Padding(email_panel, (0, 0, 2, EMAIL_INDENT))


@dataclass
class EpsteinFiles:
    all_files: list[Path]
    emails: list[Email] = field(init=False)
    iMessage_logs: list[MessengerLog] = field(init=False)
    other_files: list[Document] = field(init=False)
    emailer_counts: dict[str, int] = field(init=False)

    def __post_init__(self):
        self.emails = []
        self.iMessage_logs = []
        self.other_files = []
        self.emailer_counts = defaultdict(int)

        for file_arg in self.all_files:
            if deep_debug:
                console.print(f"\nScanning '{file_arg.name}'...")

            document = Document(file_arg)

            if document.length == 0:
                if is_debug:
                    console.print(f"   -> Skipping empty file...", style='dim')

                continue
            elif document.text[0] == '{':  # Check for JSON
                move_json_file(file_arg)
            elif MSG_REGEX.search(document.text):
                if is_debug:
                    console.print(f"   -> iMessage log file...", style='dim')

                self.iMessage_logs.append(MessengerLog(file_arg))
            else:
                emailer = None

                if DETECT_EMAIL_REGEX.match(document.text):  # Handle emails
                    email = Email(file_arg)
                    self.emails.append(email)

                    try:
                        emailer = email.author or UNKNOWN
                        self.emailer_counts[emailer.lower()] += 1

                        if deep_debug:
                            console.print(f"   -> Emailer: '{emailer}'", style='dim')

                        if len(emailer) >= 3 and emailer != UNKNOWN:
                            continue  # Don't proceed to printing debug contents if we found a valid email
                    except Exception as e:
                        console.print_exception()
                        console.print(f"\nError file '{file_arg.name}' with {document.num_lines} lines, top lines:")
                        print_top_lines(document.text)
                        raise e
                else:
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

    def print_emails_by(self, author: str | None) -> None:
        emails = self.emails_by(author)
        author = author or '[redacted]'

        if len(emails) == 0:
            logger.warning(f"No emails found for {author}")
            return

        console.print('\n\n', Panel(Text(f"{author} ({len(emails)} Emails Found)", justify='center')), '\n', style='bold reverse')

        for email in emails:
            console.print(email)

    def sorted_imessage_logs(self) -> list[MessengerLog]:
        return sorted(self.iMessage_logs, key=lambda f: f.timestamp)

    def emails_by(self, author: str | None) -> list[Email]:
        author = author.lower() if author else None
        return EpsteinFiles.sort_emails([e for e in self.emails if e.author_lowercase == author])

    @classmethod
    def sort_emails(cls, emails: list[Email]) -> list[Email]:
        return sorted(emails, key=lambda e: (e.sort_time()))


def parse_timestamp(timestamp_str: str) -> None | datetime:
    try:
        timestamp = parse(timestamp_str)
        logger.info(f'Parsed timestamp "{timestamp}" from string "{timestamp_str}"')
        return timestamp
    except Exception as e:
        logger.info(f'Failed to parse "{timestamp_str}" to timestamp!')


valid_emailer = lambda emailer: not BAD_EMAILER_REGEX.match(emailer)
