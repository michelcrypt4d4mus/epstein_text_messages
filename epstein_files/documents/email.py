import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from dateutil.parser import parse
from rich.console import Console, ConsoleOptions, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.documents.communication_document import CommunicationDocument
from epstein_files.documents.document import INFO_INDENT
from epstein_files.documents.email_header import (BAD_EMAILER_REGEX, EMAIL_SIMPLE_HEADER_REGEX, FIELD_NAMES,
     EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX, TIME_REGEX, EmailHeader)
from epstein_files.util.constant.strings import REDACTED, URL_SIGNIFIERS
from epstein_files.util.constant.names import *
from epstein_files.util.constants import *
from epstein_files.util.data import TIMEZONE_INFO, collapse_newlines, escape_single_quotes, remove_timezone, uniquify
from epstein_files.util.email_info import ConfiguredAttr
from epstein_files.util.env import logger
from epstein_files.util.file_helper import is_local_extract_file
from epstein_files.util.highlighted_group import get_style_for_name
from epstein_files.util.rich import *

DATE_REGEX = re.compile(r'(?:Date|Sent):? +(?!by|from|to|via)([^\n]{6,})\n')
BAD_TIMEZONE_REGEX = re.compile(fr'\((UTC|GMT\+\d\d:\d\d)\)|{REDACTED}')
TIMESTAMP_LINE_REGEX = re.compile(r"\d+:\d+")

DETECT_EMAIL_REGEX = re.compile(r'^(.*\n){0,2}From:')
QUOTED_REPLY_LINE_REGEX = re.compile(r'wrote:\n', re.IGNORECASE)
REPLY_TEXT_REGEX = re.compile(rf"^(.*?){REPLY_LINE_PATTERN}", re.DOTALL | re.IGNORECASE | re.MULTILINE)
BAD_LINE_REGEX = re.compile(r'^(>;?|\d{1,2}|Importance:( High)?|[iI,•]|i (_ )?i|, [-,])$')
REPLY_SPLITTERS = [f"{field}:" for field in FIELD_NAMES] + ['********************************']
LINK_LINE_REGEX = re.compile(f"^(> )?htt")

SUPPRESS_LOGS_FOR_AUTHORS = ['Undisclosed recipients:', 'undisclosed-recipients:', 'Multiple Senders Multiple Senders']
MAX_CHARS_TO_PRINT = 4000
MAX_QUOTED_REPLIES = 2
VALID_HEADER_LINES = 14

FILE_IDS_WITH_BAD_FIRST_LINES = [
    '026652',
    '029835',
    '030927',
    '031189',
]

OCR_REPAIRS: dict[str | re.Pattern, str] = {
    re.compile(r' Banno(r]?|\b)'): ' Bannon',
    re.compile(r'grnail\.com'): 'gmail.com',
    re.compile(r'gmax ?[1l] ?[@g]ellmax.c ?om'): 'gmax1@ellmax.com',
    re.compile(r"[ijlp']ee[vy]acation[©@a(&,P ]{1,3}g?mail.com"): 'jeevacation@gmail.com',
    re.compile(r"^(From|To)(: )?[_1.]{5,}", re.MULTILINE): rf"\1: {REDACTED}",  # Redacted email addresses
    'BlackBerry by AT &T': 'BlackBerry by AT&T',
    'BlackBerry from T- Mobile': 'BlackBerry from T-Mobile',
    "from my 'Phone": 'from my iPhone',
    'from Samsung Mob.le': 'from Samsung Mobile',
    # These 3 must come in this order!
    re.compile(r'([/vkT]|Ai|li|(I|7)v)rote:'): 'wrote:',
    re.compile(r"([<>.=_HIM][<>.=_HIM14]{5,}[<>.=_HIM]|MOMMINNEMUMMIN) *(wrote:?)?"): rf"{REDACTED} \2",
    re.compile(r"([,<>_]|AM|PM)\n(>)? ?wrote:?"): r'\1\2 wrote:',
    # TODO: are these necessary?
    'Torn Pritzker': TOM_PRITZKER,
    'Alireza lttihadieh': ALIREZA_ITTIHADIEH,
    'Miroslav Laj6ak': MIROSLAV_LAJCAK,
    re.compile(r'from my BlackBerry[0°] wireless device'): 'from my BlackBerry® wireless device',
    'gJeremyRubin': '@JeremyRubin',
    re.compile(r"twitter\.com[i/][lI]krauss[1lt]"): "twitter.com/lkrauss1",
    re.compile(r'timestopics/people/t/landon jr thomas/inde\n?x\n?\.\n?h\n?tml'): 'timestopics/people/t/landon_jr_thomas/index.html',
    'twitter glhsummers': 'twitter @lhsummers',
    # Subject lines
    re.compile(r"Lawyer for Susan Rice: Obama administration '?justifiably concerned' about sharing Intel with\s*Trump team -\s*POLITICO", re.I): "Lawyer for Susan Rice: Obama administration 'justifiably concerned' about sharing Intel with Trump team - POLITICO",
    re.compile(r"deadline re Mr Bradley Edwards vs Mr\s*Jeffrey Epstein", re.I): "deadline re Mr Bradley Edwards vs Mr Jeffrey Epstein",
    re.compile(r"Subject:\s*Fwd: Trending Now: Friends for three decades"): "Subject: Fwd: Trending Now: Friends for three decades",
    re.compile(r"Following Plea That Implicated Trump -\s*https://www.npr.org/676040070", re.I): "Following Plea That Implicated Trump - https://www.npr.org/676040070",
    re.compile(r"PROCEEDINGS FOR THE ST THOMAS ATTACHMENT OF\s*ALL JEFF EPSTEIN ASSETS"): "PROCEEDINGS FOR THE ST THOMAS ATTACHMENT OF ALL JEFF EPSTEIN ASSETS",
    'Sent from Mabfl': 'Sent from Mobile',  # NADIA_MARCINKO signature bad OCR
}

MARTIN_WEINBERG_SIGNATURE_PATTERN = r"Martin G. Weinberg, Esq.\n20 Park Plaza((, )|\n)Suite 1000\nBoston, MA 02116(\n61.*)?(\n.*([cC]ell|Office))*"

EMAIL_SIGNATURES = {
    ARIANE_DE_ROTHSCHILD: re.compile(r"Ensemble.*\nCe.*\ndestinataires.*\nremercions.*\nautorisee.*\nd.*\nLe.*\ncontenues.*\nEdmond.*\nRoth.*\nlo.*\nRoth.*\ninfo.*\nFranc.*\n.2.*", re.I),
    BARBRO_EHNBOM: re.compile(r"Barbro C.? Ehn.*\nChairman, Swedish-American.*\n((Office|Cell|Sweden):.*\n)*(360.*\nNew York.*)?"),
    DANNY_FROST: re.compile(r"Danny Frost\nDirector.*\nManhattan District.*\n212.*", re.IGNORECASE),
    DARREN_INDYKE: re.compile(r"DARREN K. INDYKE.*?\**\nThe information contained in this communication.*?Darren K.[\n\s]+?[Il]ndyke(, PLLC)? — All rights reserved\.? ?\n\*{50,120}(\n\**)?", re.DOTALL),
    DAVID_INGRAM: re.compile(r"Thank you in advance.*\nDavid Ingram.*\nCorrespondent\nReuters.*\nThomson.*(\n(Office|Mobile|Reuters.com).*)*"),
    DEEPAK_CHOPRA: re.compile(fr"({DEEPAK_CHOPRA}( MD)?\n)?2013 Costa Del Mar Road\nCarlsbad, CA 92009(\n(Chopra Foundation|Super Genes: Unlock.*))?(\nJiyo)?(\nChopra Center for Wellbeing)?(\nHome: Where Everyone is Welcome)?"),
    JEFFREY_EPSTEIN: re.compile(r"((\*+|please note)\n+)?(> )?(• )?(» )?The information contained in this communication is\n(> )*(» )?confidential.*?all attachments.( copyright -all rights reserved?)?", re.DOTALL),
    JESSICA_CADWELL: re.compile(r"(f.*\n)?Certified Para.*\nFlorida.*\nBURMAN.*\n515.*\nSuite.*\nWest Palm.*", re.IGNORECASE),
    KEN_JENNE: re.compile(r"Ken Jenne\nRothstein.*\n401 E.*\nFort Lauderdale.*", re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r"Please direct all scheduling.*\nFollow me on twitter.*\nwww.larrysummers.*", re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r"Lawrence (M. )?Krauss\n(Director.*\n)?(Co-director.*\n)?Foundation.*\nSchool.*\n(Co-director.*\n)?(and Director.*\n)?Arizona.*(\nResearch.*\nOri.*\n(krauss.*\n)?origins.*)?", re.IGNORECASE),
    MARTIN_WEINBERG: re.compile(fr"({MARTIN_WEINBERG_SIGNATURE_PATTERN}\n)?This Electronic Message contains.*?contents of this message is.*?prohibited.", re.DOTALL),
    PETER_MANDELSON: re.compile(r'Disclaimer This email and any attachments to it may be.*?with[ \n]+number(.*?EC4V[ \n]+6BJ)?', re.DOTALL | re.IGNORECASE),
    PAUL_BARRETT: re.compile(r"Paul Barrett[\n\s]+Alpha Group Capital LLC[\n\s]+(142 W 57th Street, 11th Floor, New York, NY 10019?[\n\s]+)?(al?[\n\s]*)?ALPHA GROUP[\n\s]+CAPITAL"),
    RICHARD_KAHN: re.compile(r'Richard Kahn[\n\s]+HBRK Associates Inc.?[\n\s]+((301 East 66th Street, Suite 1OF|575 Lexington Avenue,? 4th Floor,?)[\n\s]+)?New York, (NY|New York) 100(22|65)([\n\s]+(Tel?|Phone)( I)?[\n\s]+Fa[x"]?[\n\s]+[Ce]el?l?)?', re.IGNORECASE),
    'Susan Edelman': re.compile(r'Susan Edel.*\nReporter\n1211.*\n917.*\nsedelman.*', re.IGNORECASE),
    TERRY_KAFKA: re.compile(r"((>|I) )?Terry B.? Kafka.*\n(> )?Impact Outdoor.*\n(> )?5454.*\n(> )?Dallas.*\n((> )?c?ell.*\n)?(> )?Impactoutdoor.*(\n(> )?cell.*)?", re.IGNORECASE),
    TONJA_HADDAD_COLEMAN: re.compile(fr"Tonja Haddad Coleman.*\nTonja Haddad.*\nAdvocate Building\n315 SE 7th.*(\nSuite.*)?\nFort Lauderdale.*(\n({REDACTED} )?facsimile)?(\nwww.tonjahaddad.com?)?(\nPlease add this efiling.*\nThe information.*\nyou are not.*\nyou are not.*)?", re.IGNORECASE),
    UNKNOWN: re.compile(r"(This message is directed to and is for the use of the above-noted addressee only.*\nhereon\.)", re.DOTALL),
}

TRUNCATION_LENGTHS = {
    '023627': 15_750,  # Micheal Wolff article with brock pierce
    '030781': 1_700,
}

# Invalid for links to EpsteinWeb
JUNK_EMAILERS = [
    'asmallworld@travel.asmallworld.net',
    'editorialstaff@flipboard.com',
    'How To Academy',
    'Jokeland',
    JP_MORGAN_USGIO,
    'Saved by Internet Explorer 11',
]

TRUNCATE_ALL_EMAILS_FROM = JUNK_EMAILERS + [
    'Alan S Halperin',
    'Lvjet',
    'middle.east.update@hotmail.com',
    'Mitchell Bard',
    'Skip Rimer',
]

# These are long forwarded articles so we force a trim to 1,333 chars if these strings exist
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
    "Donald Trump's newly named chief strategist and senior counselor",
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
    # Random
    'Little Hodiaki',
    "It began with deep worries regarding China's growth path",
    'https://www.washingtonpost.com/politics/2018/09/04/transcript-phone-call',
    # Epstein
    'David Ben Gurion was asked why he, after 2000',
    # Lisa New
    'The raw materials for that period include interviews',
]

KRASSNER_RECIPIENTS = uniquify(KRASSNER_MANSON_RECIPIENTS + KRASSNER_024923_RECIPIENTS + KRASSNER_033568_RECIPIENTS)

# No point in ever displaying these; their emails show up elsewhere because they're mostly CC recipients
USELESS_EMAILERS = IRAN_NUCLEAR_DEAL_SPAM_EMAIL_RECIPIENTS + \
                   KRASSNER_RECIPIENTS + \
                   FLIGHT_IN_2012_PEOPLE + [
    'Alan Rogers',                           # Random CC
    'BS Stern',                              # A random fwd of email we have
    'Cheryl Kleen',                          # Single email from Anne Boyles, displayed under Anne Boyles
    'Connie Zaguirre',                       # Random CC
    'Dan Fleuette',                          # CC from sean bannon
    'Danny Goldberg',                        # Random Paul Krassner emails
    GERALD_LEFCOURT,                         # Single CC
    GORDON_GETTY,                            # Random CC
    JEFF_FULLER,                             # Random Jean Luc Brunel CC
    'Jojo Fontanilla',                       # Random CC
    'Joseph Vinciguerra',                    # Random CC
    'Larry Cohen',                           # Random Bill Gates CC
    'Lyn Fontanilla',                        # Random CC
    'Mark Albert',                           # Random CC
    'Matthew Schafer',                       # Random CC
    'Michael Simmons',                       # Random CC
    'Nancy Portland',                        # Lawrence Krauss CC
    'Oliver Goodenough',                     # Robert Trivers CC
    'Owen Blicksilver',                      # Landon Thomas CC
    'Peter Aldhous',                         # Lawrence Krauss CC
    ROBERT_D_CRITTON,                        # Random CC
    'Sam Harris',                            # Lawrence Krauss CC
    SAMUEL_LEFF,                             # Random CC
    "Saved by Internet Explorer 11",
    'Sean T Lehane',                         # Random CC
    'Stephen Rubin',                         # Random CC
    'Tim Kane',                              # Random CC
    'Travis Pangburn',                       # Random CC
    'Vahe Stepanian',                        # Random CC
]

# Emails sent by epstein to himself that are just notes
NOTES_TO_SELF = [
    '033274',
    '030238',
    '029752',
    '026677',
]


@dataclass
class Email(CommunicationDocument):
    actual_text: str = field(init=False)
    header: EmailHeader = field(init=False)
    is_duplicate: bool = False
    is_junk_mail: bool = False
    recipients: list[str | None] = field(default_factory=list)
    sent_from_device: str | None = None
    signature_substitution_count: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def __post_init__(self):
        super().__post_init__()

        if self.configured_attr('recipients'):
            self.recipients = EMAIL_INFO[self.file_id].recipients
        else:
            for recipient in self.header.recipients():
                self.recipients.extend(self._get_names(recipient))

        logger.debug(f"Found recipients: {self.recipients}")
        self.recipients = list(set([r for r in self.recipients if r != self.author or self.file_id in NOTES_TO_SELF]))  # Remove self CCs
        self.text = self._cleaned_up_text()
        self.actual_text = self._actual_text()
        self.sent_from_device = self._sent_from_device()
        self.is_duplicate = self.file_id in DUPLICATE_FILE_IDS
        self.is_junk_mail = self.author in JUNK_EMAILERS

    def configured_attr(self, attr: ConfiguredAttr) -> bool | datetime | str | None:
        """Find the value configured in constants.py for the 'attr' attribute of this email (if any)."""
        if self.file_id in EMAIL_INFO:
            return getattr(EMAIL_INFO[self.file_id], attr)

    def idx_of_nth_quoted_reply(self, n: int = MAX_QUOTED_REPLIES, text: str | None = None) -> int | None:
        """Get position of the nth 'On June 12th, 1985 [SOMEONE] wrote:' style line in self.text."""
        for i, match in enumerate(QUOTED_REPLY_LINE_REGEX.finditer(text or self.text)):
            if i >= n:
                return match.end() - 1

    def info_txt(self) -> Text:
        txt = Text("OCR text of email from ", style='grey46').append(self.author_txt).append(' to ')
        return txt.append(self._recipients_txt()).append(highlighter(f" probably sent at {self.timestamp}"))

    def is_local_extract_file(self) -> bool:
        return is_local_extract_file(self.filename)

    def subject(self) -> str:
        return self.header.subject or ''

    def _actual_text(self) -> str:
        """The text that comes before likely quoted replies and forwards etc."""
        if self.configured_attr('actual_text') is not None:
            return self.configured_attr('actual_text')
        elif self.header.num_header_rows == 0:
            return self.text

        text = '\n'.join(self.text.split('\n')[self.header.num_header_rows:]).strip()
        reply_text_match = REPLY_TEXT_REGEX.search(text)
        # logger.info(f"Raw text:\n" + self.top_lines(20) + '\n\n')
        # logger.info(f"With header removed:\n" + text[0:500] + '\n\n')

        if self.file_id in ['024624']:
            return text

        if reply_text_match:
            actual_num_chars = len(reply_text_match.group(1))
            actual_text_pct = f"{(100 * float(actual_num_chars) / len(text)):.1f}%"
            logger.info(f"'{self.file_path.stem}': actual_text() reply_text_match is {actual_num_chars:,} chars ({actual_text_pct} of {len(text):,})")
            text = reply_text_match.group(1)

        for field_name in REPLY_SPLITTERS:
            field_string = f'\n{field_name}'

            if field_string not in text:
                continue

            logger.debug(f"'{self.file_path.stem}': Splitting based on '{field_string.strip()}'")
            pre_from_text = text.split(field_string)[0]
            actual_num_chars = len(pre_from_text)
            actual_text_pct = f"{(100 * float(actual_num_chars) / len(text)):.1f}%"
            logger.info(f"'{self.file_path.stem}': actual_text() fwd_text_match is {actual_num_chars:,} chars ({actual_text_pct} of {len(text):,})")
            text = pre_from_text
            break

        return text.strip()

    def _border_style(self) -> str:
        """Color emails from epstein to others with the color for the first recipient."""
        if self.author == JEFFREY_EPSTEIN:
            if len(self.recipients) == 0 or self.recipients == [None]:
                style = self.author_style
            else:
                style = get_style_for_name(self.recipients[0])
        else:
            style = self.author_style

        return style.replace('bold', '').strip()

    def _cleaned_up_text(self) -> str:
        """Add newline after headers in text if actual header wasn't 'empty', remove bad lines, etc."""
        if self.header.was_initially_empty:
            text = self.text
        else:
            text = EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX.sub(r'\n\1\n', self.text).strip()

        text = '\n'.join(['' if BAD_LINE_REGEX.match(line) else line.strip() for line in text.split('\n')])
        text = REPLY_REGEX.sub(r'\n\1', text)  # Newlines between quoted replies

        for name, signature_regex in EMAIL_SIGNATURES.items():
            signature_replacement = f'<...snipped {name.lower()} legal signature...>'
            text, num_replaced = signature_regex.subn(signature_replacement, text)
            self.signature_substitution_count[name] += num_replaced

        return collapse_newlines(text).strip()

    def _extract_author(self) -> None:
        self._extract_header()

        if self.configured_attr('author'):
            self.author = EMAIL_INFO[self.file_id].author
        elif self.header.author:
            authors = self._get_names(self.header.author)
            self.author = authors[0] if (len(authors) > 0 and authors[0]) else None

    def _extract_header(self) -> None:
        """Extract an EmailHeader object from the OCR text."""
        header_match = EMAIL_SIMPLE_HEADER_REGEX.search(self.text)

        if header_match:
            self.header = EmailHeader.from_header_lines(header_match.group(0))

            if self.header.is_empty():
                self.header.repair_empty_header(self.lines)
        else:
            msg = f"No header match found in '{self.filename}'! Top lines:\n\n{self.top_lines()}"

            if self.file_id in EMAIL_INFO:
                logger.info(msg)
            else:
                logger.warning(msg)

            self.header = EmailHeader(field_names=[])

    def _extract_timestamp(self) -> datetime:
        if self.configured_attr('timestamp'):
            return EMAIL_INFO[self.file_id].timestamp
        elif self.header.sent_at:
            timestamp = _parse_timestamp(self.header.sent_at)

            if timestamp:
                return timestamp

        searchable_lines = self.lines[0:VALID_HEADER_LINES]
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
                logger.debug(f"Fell back to timestamp {timestamp} in line '{line}'...")
                return timestamp

        raise RuntimeError(f"No timestamp found in '{self.file_path.name}' top lines:\n{searchable_text}")

    def _get_names(self, emailer_str: str) -> list[str]:
        """Return a list of people's names found in 'emailer_str' (email author or recipients field)."""
        emailer_str = EmailHeader.cleanup_str(emailer_str)

        if len(emailer_str) == 0:
            return []

        names_found = [name for name, regex in EMAILER_REGEXES.items() if regex.search(emailer_str)]

        if BAD_EMAILER_REGEX.match(emailer_str) or TIME_REGEX.match(emailer_str):
            if len(names_found) == 0 and emailer_str not in SUPPRESS_LOGS_FOR_AUTHORS:
                logger.warning(f"'{self.filename}': No emailer found in '{escape_single_quotes(emailer_str)}'")
            else:
                logger.info(f"Extracted {len(names_found)} names from semi-invalid '{emailer_str}': {names_found}...")

            return names_found

        names_found = names_found or [emailer_str]
        return [_reverse_first_and_last_names(name) for name in names_found]

    def _recipients_txt(self) -> Text:
        """Text object with comma separated colored versions of all recipients."""
        recipients = [r or UNKNOWN for r in self.recipients] if len(self.recipients) > 0 else [UNKNOWN]

        # Use just the last name for each recipient if there's 3 or more recipients
        return join_texts([
            Text(r if (' ' not in r or len(recipients) < 3) else r.split()[-1], style=get_style_for_name(r))
            for r in recipients
        ], join=', ')

    def _repair(self) -> None:
        """Repair particularly janky files."""
        if self.file_id in FILE_IDS_WITH_BAD_FIRST_LINES:
            self.text = '\n'.join(self.lines[1:])
        elif self.file_id == '029977':
            self.text = self.text.replace('Sent 9/28/2012 2:41:02 PM', 'Sent: 9/28/2012 2:41:02 PM')
        elif self.file_id == '031442':
            self.lines = [self.lines[0] + self.lines[1]] + self.lines[2:]
            self.text = '\n'.join(self.lines)

        lines = self.regex_repair_text(OCR_REPAIRS, self.text).split('\n')
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if LINK_LINE_REGEX.search(line):
                if 'htm' not in line \
                         and i < (len(lines) - 1) \
                         and (lines[i + 1].endswith('/') or any(s in lines[i + 1] for s in URL_SIGNIFIERS)):
                    logger.info(f"{self.filename}: Joining lines\n   1. {line}\n   2. {lines[i + 1]}\n")
                    line += lines[i + 1]
                    i += 1

                line = line.replace(' ', '')

            new_lines.append(line)
            i += 1

        self.text = '\n'.join(new_lines)
        self._set_computed_fields()

    def _sent_from_device(self) -> str | None:
        """Find any 'Sent from my iPhone' style lines if they exist."""
        sent_from_match = SENT_FROM_REGEX.search(self.actual_text)

        if sent_from_match:
            sent_from = sent_from_match.group(0)
            return 'S' + sent_from[1:] if sent_from.startswith('sent') else sent_from

    def __rich_console__(self, _console: Console, _options: ConsoleOptions) -> RenderResult:
        logger.debug(f"Printing '{self.filename}'...")

        if self.file_id in DUPLICATE_FILE_IDS:
            yield self.duplicate_file_txt()
            yield Text('')
            return

        yield self.file_info_panel()
        text = self.text
        quote_cutoff = self.idx_of_nth_quoted_reply(text=text)  # Trim if there's many quoted replies
        num_chars = MAX_CHARS_TO_PRINT
        trim_footer_txt = None

        if self.file_id in TRUNCATION_LENGTHS:
            num_chars = TRUNCATION_LENGTHS[self.file_id]
        elif self.author in TRUNCATE_ALL_EMAILS_FROM or any((term in self.text) for term in TRUNCATE_TERMS):
            num_chars = int(MAX_CHARS_TO_PRINT / 3)
        elif quote_cutoff and quote_cutoff < MAX_CHARS_TO_PRINT:
            num_chars = quote_cutoff

        if len(text) > num_chars:
            text = text[0:num_chars]
            epsteinify_link_markup = epsteinify_doc_link_markup(self.url_slug, self.author_style)
            trim_note = f"<...trimmed to {num_chars} characters of {self.length}, read the rest at {epsteinify_link_markup}...>"
            trim_footer_txt = Text.from_markup(wrap_in_markup_style(trim_note, 'dim'))

        panel_txt = highlighter(text)

        if trim_footer_txt:
            panel_txt.append('\n\n').append(trim_footer_txt)

        email_txt_panel = Panel(panel_txt, border_style=self._border_style(), expand=False)
        yield Padding(email_txt_panel, (0, 0, 1, INFO_INDENT))


def _parse_timestamp(timestamp_str: str) -> None | datetime:
    try:
        timestamp_str = timestamp_str.replace('(GMT-05:00)', 'EST')
        timestamp_str = BAD_TIMEZONE_REGEX.sub(' ', timestamp_str).strip()
        timestamp = parse(timestamp_str, tzinfos=TIMEZONE_INFO)
        logger.debug(f'Parsed timestamp "%s" from string "%s"', timestamp, timestamp_str)
        return remove_timezone(timestamp)
    except Exception as e:
        logger.debug(f'Failed to parse "{timestamp_str}" to timestamp!')


def _reverse_first_and_last_names(name: str) -> str:
    if '@' in name:
        return name.lower()

    if ', ' in name:
        names = name.split(', ')
        return f"{names[1]} {names[0]}"
    else:
        return name
