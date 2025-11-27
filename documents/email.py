import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from dateutil.parser import parse
from dateutil import tz
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markup import escape
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from documents.document import FALLBACK_TIMESTAMP, CommunicationDocument
from documents.email_header import AUTHOR, EMAIL_SIMPLE_HEADER_REGEX, EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX, TO_FIELDS, EmailHeader
from util.constants import *
from util.env import is_debug, is_fast_mode, logger
from util.rich import *
from util.strings import *

TIME_REGEX = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}|Thursday|Monday|Tuesday|Wednesday|Friday|Saturday|Sunday).*')
DATE_REGEX = re.compile(r'(?:Date|Sent):? +(?!by|from|to|via)([^\n]{6,})\n')
TIMESTAMP_LINE_REGEX = re.compile(r"\d+:\d+")
PACIFIC_TZ = tz.gettz("America/Los_Angeles")
TIMEZONE_INFO = {"PST": PACIFIC_TZ, "PDT": PACIFIC_TZ}  # Suppresses annoying warnings from parse() calls

EMAIL_REGEX = re.compile(r'From: (.*)')
EMAIL_HEADER_REGEX = re.compile(r'^(((Date|Subject):.*\n)*From:.*\n((Date|Sent|To|CC|Importance|Subject|Attachments):.*\n)+)')
DETECT_EMAIL_REGEX = re.compile('^(From:|.*\nFrom:|.*\n.*\nFrom:)')
BAD_EMAILER_REGEX = re.compile(r'^>|agreed|ok|sexy|rt|re:|fwd:|((sent|attachments|subject|importance).*|.*(11111111|january|201\d|hysterical|i have|image0|so that people|article 1.?|momminnemummin|These conspiracy theories|your state|undisclosed|www\.theguardian|talk in|it was a|what do|cc:|call (back|me)).*)$', re.IGNORECASE)
EMPTY_HEADER_REGEX = re.compile(r'^\s*From:\s*\n((Date|Sent|To|CC|Importance|Subject|Attachments):\s*\n)+')
SKIP_HEADER_ROW_REGEX = re.compile(r"^(agreed|call me|Hysterical|schwartman).*")

# TODO: fill out the regex for reply lines like: 'In a message dated 1/12/2012 10:21:24 A.M. Eastern Standard Time, jeevacation@gmail.com writes:'
REPLY_LINE_IN_A_MSG_PATTERN = r"In a message dated \d+/\d+/\d+.*writes:"
REPLY_LINE_ENDING_PATTERN = r"[_ \n](AM|PM|[<_]|wrote:?)"
REPLY_LINE_ON_NUMERIC_DATE_PATTERN = fr"On \d+/\d+/\d+[, ].*{REPLY_LINE_ENDING_PATTERN}"
REPLY_LINE_ON_DATE_PATTERN = fr"On (\d+ )?((Mon|Tues?|Wed(nes)?|Thu(rs)?|Fri|Sat(ur)?|Sun)(day)?|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*).*{REPLY_LINE_ENDING_PATTERN}"
FORWARDED_LINE_PATTERN = r"-+ ?(Forwarded|Original)\s*Message ?-*|Begin forwarded message:?"
REPLY_LINE_PATTERN = rf"({REPLY_LINE_IN_A_MSG_PATTERN}|{REPLY_LINE_ON_NUMERIC_DATE_PATTERN}|{REPLY_LINE_ON_DATE_PATTERN}|{FORWARDED_LINE_PATTERN})"
REPLY_REGEX = re.compile(REPLY_LINE_PATTERN, re.IGNORECASE)
REPLY_TEXT_REGEX = re.compile(rf"^(.*?){REPLY_LINE_PATTERN}", re.IGNORECASE | re.DOTALL)
SENT_FROM_REGEX = re.compile(r'^(?:Please forgive typos. |Sorry for all the typos .)?(Sent (from|via).*(and string|AT&T|Droid|iPad|Phone|Mail|BlackBerry(.*(smartphone|device|Handheld|AT&T|T- ?Mobile))?)\.?)', re.M | re.I)
QUOTED_REPLY_LINE_REGEX = re.compile(r'wrote:\n', re.IGNORECASE)
NOT_REDACTED_EMAILER_REGEX = re.compile(r'saved by internet', re.IGNORECASE)
BAD_LINE_REGEX = re.compile(r'^(\d{1,2}|Importance:( High)?|I)$')
UNKNOWN_SIGNATURE_REGEX = re.compile(r"(This message is directed to and is for the use of the above-noted addressee only.*\nhereon\.)", re.DOTALL)

CLIPPED_SIGNATURE_REPLACEMENT = '[dim]<...snipped epstein legal signature...>[/dim]'
UNDISCLOSED_RECIPIENTS_REGEX = re.compile(r'Undisclosed[- ]recipients:', re.IGNORECASE)
BAD_FIRST_LINES = ['026652', '029835', '031189']
MAX_CHARS_TO_PRINT = 4000
VALID_HEADER_LINES = 14
EMAIL_INDENT = 3

clipped_signature_replacement = lambda name: f'[dim]<...snipped {name.lower()} legal signature...>[/dim]'

KNOWN_TIMESTAMPS = {
    '028851': datetime(2014, 4, 27, 6, 00),
    '028849': datetime(2014, 4, 27, 6, 30),
    '032475': datetime(2017, 2, 15, 13, 31, 25),
    '030373': datetime(2018, 10, 3, 1, 49, 27),
}

OCR_REPAIRS: dict[str | re.Pattern, str] = {
    'BlackBerry by AT &T': 'BlackBerry by AT&T',
    'BlackBerry from T- Mobile': 'BlackBerry from T-Mobile',
    "Sent from my 'Phone": 'Sent from my iPhone',
    'Sent from Samsung Mob.le': 'Sent from Samsung Mobile',
    'Sent from Mabfl': 'Sent from Mobile',
    'Torn Pritzker': 'Tom Pritzker',
    'Alireza lttihadieh': ALIREZA_ITTIHADIEH,
    'Miroslav Laj6ak': MIROSLAV,
    re.compile(r'([/vkT]|Ai|li|(I|7)v)rote:'): 'wrote:',
    re.compile(r'timestopics/people/t/landon jr thomas/inde\n?x\n?\.\n?h\n?tml'): 'timestopics/people/t/landon_jr_thomas/index.html',
    re.compile(r"([<>.=_HIM][<>.=_HIM14]{5,}[<>.=_HIM]|MOMMINNEMUMMIN) *(wrote:?)?"): rf"{REDACTED} \2",
    re.compile(r"([,<>_]|AM|PM)\n(>)? ?wrote:?"): r'\1\2 wrote:',
}

TRUNCATE_ALL_EMAILS_FROM = [
    'middle.east.update@hotmail.com',
    'Mitchell Bard',
    'us.gio@jpmorgan.com',
]

# These are long forwarded articles we don't want to display over and over
TRUNCATE_TERMS = [
    'The rebuilding of Indonesia',
    'Dominique Strauss-Kahn',
    'THOMAS L. FRIEDMAN',
    'a sleek, briskly paced film whose title suggests a heist movie',
    'quote from The Colbert Report distinguishes',
    'co-inventor of the GTX Smart Shoe',
    'my latest Washington Post column',
    'Whether you donated to Poetry in America through',
    'supported my humanities work at Harvard',
    'Calendar of Major Events, Openings, and Fundraisers',
    'Nuclear Operator Raises Alarm on Crisis',
    'as responsible for the democratisation of computing and',
    'AROUND 1,000 operational satellites are circling the Earth',
    "In recent months, China's BAT collapse",
    'President Obama introduces Jim Yong Kim as his nominee',
    'Trump appears with mobster-affiliated felon at New',
    'Lead Code Enforcement Walton presented the facts',
    "Is UNRWA vital for the Palestinians' future",
    'The New York company, led by Stephen Ross',
    'I spent some time mulling additional aspects of a third choice presidential',
    'you are referring to duplication of a gene',
    'i am writing you both because i am attaching a still not-quite-complete response',
    'Learn to meditate and discover what truly nourishes your entire being',
    'Congratulations to the 2019 Hillman Prize recipients',
    'This much we know - the Fall elections are shaping up',
    "Special counsel Robert Mueller's investigation may face a serious legal obstacle",
    "nearly leak-proof since its inception more than a year ago",
    "I appreciate the opportunity to respond to your email",
    "Hello Peter. I am currently on a plane. I sent you earlier",
    "I appreciate the opportunity to respond to your email",
    'I just wanted to follow up on a couple of notes. I have been coordinating with Richard Kahn',
    'So, Peggy, if you could just let me know what info to include on the donation',
    'Consult a lawyer beforehand, if possible, but be cooperative/nice at this stage',
    # Amanda Ens
    'We remain positive on banks that can make acceptable returns',
    'David Woo (BAML head of FX, Rates and EM Strategy, very highly regarded',
    "Please let me know if you're interested in joining a small group meeting",
    'Erika Najarian, BAML financials research analyst, just returned',
    'We can also discuss single stock and Topix banks',
    'We are recording unprecedented divergences in falling equity vol',
    'As previously discussed between you and Ariane',
    'The US trade war against China: The view from Beijing',
    'no evidence you got the latest so i have sent you just the key message',
    # Joscha Bach
    'Cells seem to be mostly indistinguishable (except',
    'gender differenece. unlikely motivational, every cell is different',
    'Some thoughts I meant to send back for a long time',
    # Krassner
    'My friend Michael Simmons, who has been the editor of National Lampoon',
    "In the premiere episode of 'The Last Laugh' podcast, Sarah Silverman",
    'Thanks so much for sharing both your note to Steven and your latest Manson essay',
    # Edward Larson
    'Coming from an international background, and having lived in Oslo, Tel Aviv',
    # Katherine Keating
    'Paul Keating is aware that many people see him as a puzzle and contradiction',
    'his panoramic view of world affairs sharper than ever, Paul Keating blames',
    # melanie
    'Some years ago when I worked at the libertarian Cato Institute'
    # rich kahn
    'House and Senate Republicans on their respective tax overhaul',
    'The Tax Act contains changes to the treatment of "carried interests"',
    'General Election: Trump vs. Clinton LA Times/USC Tracking',
    'Location: Quicken Loans Arena in Cleveland, OH',
    'A friendly discussion about Syria with a former US State Department',
    # Tom / Paul Krassner
    'I forgot to post my cartoon from week before last, about Howard Schultz',
    # Bannon
    "Bannon the European: He's opening the populist fort in Brussels",
    "Steve Bannon doesn't do subtle.",
    'The Department of Justice lost its latest battle with Congress',
    # Diane Ziman
    'I was so proud to see him speak at the Women',
    # Krauss
    'On confronting dogma, I of course agree',
    'I did neck with that woman, but never forced myself on her',
    'It is hard to know how to respond to a list of false',
    'The Women in the World Summit opens April 12',
    'lecture in Heidelberg Oct 14 but they had to cancel',
    # Nikolic
    'people from LifeBall',
]

# No point in ever displaying these
USELESS_EMAILERS = [
    'asmallworld@travel.asmallworld.net',  # Promo travel stuff
    'digest-noreply@quora.com',
    'editorialstaff@flipboard.com',
    'How To Academy',
    'Jokeland',
    'Saved by Internet Explorer 11',
]

SUPPRESS_OUTPUT_FOR_IDS = {
    '026499': "it's quoted in full in 026298",
    '033207': "it's the same as 033580",
    '028765': "it's the same as 027053",
}


@dataclass
class Email(CommunicationDocument):
    author_lowercase: str | None = field(init=False)
    header: EmailHeader = field(init=False)
    recipients: list[str | None] = field(default_factory=list)
    sent_from_device: str | None = None

    def __post_init__(self):
        super().__post_init__()
        self._repair()
        self._extract_header()

        if is_fast_mode:
            self.author = UNKNOWN
            return

        if self.file_id in KNOWN_EMAIL_AUTHORS:
            self.author = KNOWN_EMAIL_AUTHORS[self.file_id]
        elif not self.header.author:
            self.author = None
        else:
            authors = self._get_names(self.header.author)
            self.author = authors[0] if len(authors) > 0 else None

            if len(authors) == 0:
                logger.info(f"No authors found in '{self.header.author}'!")

        if self.file_id in KNOWN_EMAIL_RECIPIENTS:
            recipient = KNOWN_EMAIL_RECIPIENTS[self.file_id]
            self.recipients = recipient if isinstance(recipient, list) else [recipient]
        else:
            self.recipients = []

            for recipient in ((self.header.to or []) + (self.header.cc or []) + (self.header.bcc or [])):
                self.recipients += self._get_names(recipient)

        logger.debug(f"Found recipients: {self.recipients}")
        self.recipients = list(set([r for r in self.recipients if r != self.author]))  # Remove self CCs
        self.recipients_lower = [r.lower() if r else None for r in self.recipients]
        recipients = self.recipients if len(self.recipients) > 0 else [UNKNOWN]
        self.recipient_txt = Text('')

        for i, recipient in enumerate(recipients):
            if i > 0:
                self.recipient_txt.append(', ')

            recipient = recipient or UNKNOWN
            recipient_str = recipient if (' ' not in recipient or len(recipients) < 3) else recipient.split()[-1]
            self.recipient_txt.append(recipient_str, style=COUNTERPARTY_COLORS.get(recipient, DEFAULT))

        self.timestamp = self._extract_sent_at()
        self.author_lowercase = self.author.lower() if self.author else None
        self.author_style = COUNTERPARTY_COLORS.get(self.author or UNKNOWN, DEFAULT)
        self.author_txt = Text(self.author or UNKNOWN, style=self.author_style)
        self.archive_link = self.epsteinify_link(self.author_style)
        self.epsteinify_link_markup = make_link_markup(self.epsteinify_name_url, self.file_path.stem, self.author_style)
        self.sent_from_device = self._sent_from_device()

    def description(self) -> Text:
        if is_fast_mode:
            return Text(self.filename)
        else:
            info_str = f"Email (author='{self.author}', recipients={self.recipients}, timestamp='{self.timestamp}')"
            return Text.from_markup(highlight_text(info_str))

    def idx_of_nth_quoted_reply(self, n: int = 2, text: str | None = None) -> int | None:
        text = text or self.text

        for i, match in enumerate(QUOTED_REPLY_LINE_REGEX.finditer(text)):
            if i >= n:
                return match.end() - 1

    def _border_style(self) -> str:
        if self.author == JEFFREY_EPSTEIN:
            if len(self.recipients) == 0:
                return self.author_style
            else:
                return COUNTERPARTY_COLORS[self.recipients[0] or UNKNOWN]
        else:
            return self.author_style

    def _cleaned_up_text(self) -> str:
        # add newline after header if header looks valid
        if not EMPTY_HEADER_REGEX.search(self.text):
            text = EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX.sub(r'\n\1\n', self.text).strip()
        else:
            text = self.text

        text = '\n'.join([line for line in text.split('\n') if not BAD_LINE_REGEX.match(line)])
        text = escape(REPLY_REGEX.sub(r'\n\1', text))  # Newlines between quoted replies

        for name, signature_regex in EMAIL_SIGNATURES.items():
            text = signature_regex.sub(clipped_signature_replacement(name), text)

        return text

    def _extract_sent_at(self) -> datetime:
        if self.file_id in KNOWN_TIMESTAMPS:
            return KNOWN_TIMESTAMPS[self.file_id]

        searchable_lines = self.text.split('\n')[0:VALID_HEADER_LINES]
        searchable_text = '\n'.join(searchable_lines)
        date_match = DATE_REGEX.search(searchable_text)

        if date_match:
            timestamp = _parse_timestamp(date_match.group(1))

            if timestamp:
                return timestamp

        logger.debug(f"Failed to find timestamp, falling back to parsing {VALID_HEADER_LINES} lines...")

        for line in searchable_lines:
            if not TIMESTAMP_LINE_REGEX.search(line):
                continue

            timestamp = _parse_timestamp(line)

            if timestamp:
                logger.info(f"Fell back to timestamp {timestamp} in line '{line}'...")
                return timestamp

        self.log_top_lines(msg="No valid timestamp found in email!")
        raise RuntimeError(f"No timestamp found in '{self.file_path.name}'")

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
                    log_prefix = f"Looks like '{value}' is a mismatch for '{field_name}', " if is_debug else ''

                    if field_name == AUTHOR:
                        if SKIP_HEADER_ROW_REGEX.match(value):
                            logger.info(f"{log_prefix}, trying the next line...")
                            num_headers += 1
                            value = self.lines[i + num_headers]
                        elif TIME_REGEX.match(value) or value == 'Darren,' or BAD_EMAILER_REGEX.match(value):
                            logger.info(f"{log_prefix}, decrementing num_headers and skipping...")
                            num_headers -= 1
                            continue
                    elif field_name in TO_FIELDS:
                        if TIME_REGEX.match(value):
                            logger.info(f"{log_prefix}, trying next line...")
                            num_headers += 1
                            value = self.lines[i + num_headers]
                        elif BAD_EMAILER_REGEX.match(value):
                            logger.info(f"{log_prefix}, decrementing num_headers and skipping...")
                            num_headers -= 1
                            continue

                        value = [v.strip() for v in value.split(';') if len(v.strip()) > 0]

                    setattr(self.header, field_name, value)

                logger.debug(f"Corrected empty header to:\n{self.header}\n\nTop rows of file\n\n{self.top_lines((num_headers + 1) * 2)}")
            else:
                logger.debug(f"Extracted email header:\n{self.header}")
        else:
            if not (self.file_id in KNOWN_EMAIL_AUTHORS and self.file_id in KNOWN_EMAIL_RECIPIENTS):
                logger.warning(f"No header match found in '{self.filename}'! Top lines:\n\n{self.top_lines()}")

            self.header = EmailHeader(field_names=[])

    def _get_names(self, emailer_str: str) -> list[str]:
        if emailer_str.rstrip('<').strip() == REDACTED:  # TODO: this sucks, just for HOUSE_OVERSIGHT_022187
            return []

        emailer_str = EmailHeader.cleanup_str(emailer_str)
        names = []

        for name, regex in EMAILER_REGEXES.items():
            if regex.search(emailer_str):
                names.append(name)

        if BAD_EMAILER_REGEX.match(emailer_str) or TIME_REGEX.match(emailer_str):
            log_msg = f"'{self.filename}': No valid emailer found in '{escape_single_quotes(emailer_str)}'"

            if UNDISCLOSED_RECIPIENTS_REGEX.match(emailer_str) and len(names) == 0:
                logger.debug(log_msg)
            elif len(names) == 0:
                logger.warning(log_msg)
            else:
                logger.info(f"Extracted {len(names)} emailers from semi-invalid '{emailer_str}': {names}...")

            return names

        if len(names) == 0:
            names.append(emailer_str)
        elif len(names) > 1:
            logger.info(f"Found more than 1 emailer in '{emailer_str}': {names}")

        return [_reverse_first_and_last_names(name) for name in names]

    def _repair(self) -> None:
        """Repair particularly janky files."""
        if self.lines[0].startswith('Grant_Smith066474"eMailContent.htm') or self.file_id in BAD_FIRST_LINES:
            self.text = '\n'.join(self.lines[1:])
        elif self.file_id == '029977':
            self.text = self.text.replace('Sent 9/28/2012 2:41:02 PM', 'Sent: 9/28/2012 2:41:02 PM')
        elif self.file_id == '031442':
            self.lines = [self.lines[0] + self.lines[1]] + self.lines[2:]
            self.text = '\n'.join(self.lines)

        self.text = self.regex_repair_text(OCR_REPAIRS, self.text)
        self._set_computed_fields()

    def _sent_from_device(self) -> str | None:
        reply_text_match = REPLY_TEXT_REGEX.search(self.text)
        text = reply_text_match.group(1) if reply_text_match else self.text
        sent_from_match = SENT_FROM_REGEX.search(text)

        if sent_from_match:
            sent_from = sent_from_match.group(0)
            return 'S' + sent_from[1:] if sent_from.startswith('sent') else sent_from

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        if self.file_id in SUPPRESS_OUTPUT_FOR_IDS:
            txt = Text(f"Not showing ", style='dim').append(self.filename, style='cyan')
            yield txt.append(f" because {SUPPRESS_OUTPUT_FOR_IDS[self.file_id]}").append('\n')
            return

        yield Panel(self.archive_link, border_style=self._border_style(), expand=False)
        info_line = Text("OCR text of email from ", style='grey46').append(self.author_txt).append(f' to ')
        info_line.append(self.recipient_txt).append(f" probably sent at ")
        info_line.append(f"{self.timestamp or '?'}", style='spring_green3')
        yield Padding(info_line, (0, 0, 0, EMAIL_INDENT))
        text = self._cleaned_up_text()
        quote_cutoff = self.idx_of_nth_quoted_reply(text=text)
        num_chars = MAX_CHARS_TO_PRINT

        if self.author in TRUNCATE_ALL_EMAILS_FROM or any((term in self.text) for term in TRUNCATE_TERMS):
            num_chars = int(MAX_CHARS_TO_PRINT / 3)
        elif quote_cutoff and quote_cutoff < MAX_CHARS_TO_PRINT:
            logger.debug(f"Found {self.count_regex_matches(QUOTED_REPLY_LINE_REGEX.pattern)} quotes, cutting off at char {quote_cutoff}")
            num_chars = quote_cutoff

        if len(text) > num_chars:
            text = text[0:num_chars]
            text += f"\n\n[dim]<...trimmed to {num_chars} characters of {self.length}, read the rest: {self.epsteinify_link_markup}...>[/dim]"

        text = REPLY_REGEX.sub(rf'[{HEADER_STYLE}]\1[/{HEADER_STYLE}]', text)
        text = SENT_FROM_REGEX.sub(fr'[{SENT_FROM}]\1[/{SENT_FROM}]', text)
        text = UNKNOWN_SIGNATURE_REGEX.sub(r'[dim]\1[/dim]', text)
        yield Padding(Panel(highlight_text(text), border_style=self._border_style(), expand=False), (0, 0, 2, EMAIL_INDENT))


def _parse_timestamp(timestamp_str: str) -> None | datetime:
    try:
        timestamp_str = timestamp_str.replace(' (GMT-05:00)', 'EST').replace(' (UTC)', '')
        timestamp_str = timestamp_str.replace(' (GMT+07:00)', '')  # TODO: fix
        timestamp = parse(timestamp_str.replace(REDACTED, ' ').strip(), tzinfos=TIMEZONE_INFO)
        logger.debug(f'Parsed timestamp "{timestamp}" from string "{timestamp_str}"')

        if timestamp.tzinfo:
            timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
            logger.debug(f"    -> Converted to UTC: {timestamp}")

        return timestamp
    except Exception as e:
        logger.debug(f'Failed to parse "{timestamp_str}" to timestamp!')


def _reverse_first_and_last_names(name: str) -> str:
    if ', ' in name:
        names = name.split(', ')
        return f"{names[1]} {names[0]}"
    else:
        return name
