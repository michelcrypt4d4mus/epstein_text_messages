import json
import logging
import re
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, cast, TypeVar

from dateutil.parser import parse
from rich import box
from rich.console import Console, ConsoleOptions, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.communication import Communication
from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, EXCERPT_STYLE
from epstein_files.documents.documents.categories import Uninteresting
from epstein_files.documents.config.doc_cfg import DEFAULT_TRUNCATE_TO, NO_TRUNCATE, SHORT_TRUNCATE_TO, DebugDict, Metadata
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.emails.constants import *
from epstein_files.documents.emails.email_parts import EmailParts
from epstein_files.documents.emails.email_header import (EMAIL_SIMPLE_HEADER_REGEX,
     EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX, EmailHeader)
from epstein_files.documents.emails.emailers import IDENTIFYING_REGEXES, IDENTIFIER_FALSE_ALARMS, extract_emailer_names
from epstein_files.documents.other_file import OtherFile
from epstein_files.people.entity import Entity, EntityScanArg
from epstein_files.people.interesting_people import EMAILERS_OF_INTEREST_SET
from epstein_files.people.names import sort_names
from epstein_files.output.epstein_highlighter import highlighter
from epstein_files.output.highlight_config import HIGHLIGHTED_NAMES, get_style_for_name
from epstein_files.output.html.builder import table_to_html
from epstein_files.output.html.positioned_rich import to_em
from epstein_files.output.layout_elements.file_display import FileDisplay, JustifyMethod
from epstein_files.output.rich import DEFAULT_TABLE_KWARGS, build_table, styled_key_value
from epstein_files.util.constant.strings import APPEARS_IN, ARCHIVE_LINK_COLOR, REDACTED, TIMESTAMP_DIM, OcrRepair
from epstein_files.util.constant.urls import URL_SIGNIFIERS
from epstein_files.util.constants import CONFIGS_BY_ID
from epstein_files.util.env import args, site_config
from epstein_files.util.helpers.data_helpers import (AMERICAN_TIME_REGEX, TIMEZONE_INFO, CharRange, coerce_utc, flatten,
     prefix_keys, uniq_sorted, uniquify, without_falsey)
from epstein_files.util.helpers.rich_helpers import enclose
from epstein_files.util.external_link import join_texts, link_text_obj
from epstein_files.util.helpers.string_helper import capitalize_first, collapse_newlines, is_bool_prop, quote, strip_pdfalyzer_panels
from epstein_files.util.logging import logger

# Email bod regexes
BAD_FIRST_LINE_REGEX = re.compile(r'^(>>|Grant_Smith066474"eMailContent.htm|LOVE & KISSES)$')
BAD_LINE_REGEX = re.compile(r'^([>=];?|[>»]*=20|\d{1,2}|PAGE INTENTIONALLY LEFT BLANK|Classification: External Communication|Hide caption|Importance:?\s*High|[iI,•]|[1i] (_ )?[il]|, [-,]|L\._|_filtered|si.nature.asc|.*(yiv0232|font-family:|margin-bottom:).*)$')
BAD_SUBJECT_CONTINUATIONS = ['orwarded', 'Hi ', 'Sent ', 'AmLaw', 'Original Message', 'Privileged', 'Sorry', '---']
LINK_LINE_REGEX = re.compile(r"^[>• ]*htt")
LINK_LINE2_REGEX = re.compile(r"^[-\w.%&=/]{5,}$")
QUOTED_REPLY_LINE_REGEX = re.compile(r'(\nFrom:(.*)|wrote:)\n', re.IGNORECASE)
REPLY_TEXT_REGEX = re.compile(rf"^(.*?){REPLY_LINE_PATTERN}", re.DOTALL | re.IGNORECASE | re.MULTILINE)
XML_PLIST_REGEX = re.compile(r"[<=]?\?xml version.*</(plist|xml)>", re.DOTALL)

# Timestamp regexes
BAD_TIMEZONE_REGEX = re.compile(fr'\((UTC|GMT\+\d\d:\d\d)\)|{REDACTED}')
DATE_HEADER_REGEX = re.compile(r'(?:Date|Sent):? +(?!by|from|to|via)([^\n]{6,})\n')
TIMESTAMP_LINE_REGEX = re.compile(r"\d+:\d+")

# numbers
MAX_NUM_HEADER_LINES = 14
MAX_QUOTED_REPLIES = 1
NUM_LINES_TO_REPAIR_HEADERS = 6
NUM_WORDS_IN_LAST_QUOTE = 6

# TODO: Copy display_text?
DERIVED_CFG_PROPS_TO_COPY = [
    'author_uncertain',
    'category',
    'is_in_chrono',
    'is_interesting',
]

# Junk mail
JUNK_EMAILERS = [
    entity.name
    for junk_hg in HIGHLIGHTED_NAMES if junk_hg.label == Uninteresting.JUNK
    for entity in junk_hg.entities
]

BCC_LISTS = JUNK_EMAILERS + MAILING_LISTS
TRUNCATE_EMAILS_BY = BCC_LISTS + TRUNCATE_EMAILS_FROM
EMAILERS_TO_ALWAYS_TRUNCATE = set(BCC_LISTS + TRUNCATE_EMAILS_BY)
REWRITTEN_HEADER_MSG = "(janky OCR header fields were prettified, check source if something seems off)"

# TODO: add other forward patterns
REPLY_SPLITTERS = [f"{field}:" for field in COMMON_HEADER_FIELDS] + [
    '********************************',
    'Begin forwarded message',
]

OCR_REPAIRS: OcrRepair = {
    # '­': '-',
    # '‐': '-',
    '-­‐': '-',  # TODO: weird hyphens in 027004 and other files that rich doesn't handle well
    re.compile('»'): '>>',
    re.compile(r'grnail\.com'): 'gmail.com',
    'Newsmax. corn': 'Newsmax.com',
    # These 3 must come in this order!
    re.compile(r'([/vkT]|Ai|li|(I|7)v)rote:'): 'wrote:',
    re.compile(r"([<.=_HIM][<>.=_HIM14]{5,}[<>.=_HIM]|MOMMINNEMUMMIN) *(wrote:?)?"): rf"{REDACTED} \2",
    re.compile(r"([,<>_]|AM|PM)\n(>)? ?wrote:?"): r'\1\2 wrote:',
    # Headers
    re.compile(r"^From "): 'From: ',  # first line only
    re.compile(r"^((From|To):? ?)[_1.]{5,}", re.MULTILINE): rf"\1: {REDACTED}",  # Redacted email addresses
    re.compile(fr"^(From|To) ?{REDACTED}", re.MULTILINE): fr"\1: {REDACTED}",
    re.compile(r"I ?(od|nl)ine-Images:"): 'Inline-Images:',
    re.compile(r"^((?:B?cc|To):.*)\n(>?;.*)", re.IGNORECASE | re.MULTILINE): r'\1 \2',
    re.compile(r"^(Sent|Subject) (?![Ff]rom|on|using|[Rr]emote|[Vv]ia|with)", re.MULTILINE): r'\1: ',
    re.compile(r"^Subject[.•]{,2} ", re.MULTILINE): 'Subject: ',
    re.compile(r"^(Forwarded|Original) Message$", re.IGNORECASE | re.MULTILINE): r"--- \1 Message ---",  # Make forward lines match our highlight
    # Excessive quote chars
    re.compile(r"wrote:\n[>»]+(\n[>»]+)"): r"wrote:\1",
    re.compile(r"(^[>»]+\n){2,}", re.MULTILINE): r"\1",
    re.compile(r"\n[<>I ]*wrote:"): ' wrote:',
    # HTML garbage
    '&lt;': '<',
    re.compile(r'(fi|[&S5d])gt;'): '>',
    re.compile(r'[</=]{,3}(cl|d)?iv>|&[=n]bs[=p];|<=span>|=C\d+\b'): '',
    re.compile(r'^O= ', re.MULTILINE): 'On ',
    re.compile(r"<?=/?[bru]>"): '',
    re.compile(r'(^|\s)[<=][AC]\d+[=>]?', re.MULTILINE): r'\1',
    re.compile(r'[<=]=?/?(br|d?iv)( (class|id)="\w+")?>'): '',
    re.compile(r"\n<mailt.:?(.{,25})[»>]\s*wrote"): r'\1 wrote',
    re.compile(r"^--\w+-- (conversation-id|date-last-viewed).*(flags|remote-id\s\d+)(\s*\d{6,}.*remote-id.*\d+)?", re.MULTILINE): '',
    re.compile(r"<mailto:([-\w=.@]+)[»>]"): r'\1',
    # Names / email addresses
    r'Alireza lttihadieh': ALIREZA_ITTIHADIEH,
    r'bamaby': 'barnaby',
    r'Miroslav Laj6ak': MIROSLAV_LAJCAK,
    r'Ross G°w': ROSS_GOW,
    r'Torn Pritzker': TOM_PRITZKER,
    re.compile(r"( [AP]M,)\s+wrote:$", re.MULTILINE): r'\1 <REDACTED> wrote:',
    re.compile(r' Banno(r]?|\b)'): ' Bannon',
    re.compile(r"\bBamaby\b"): 'Barnaby',
    re.compile(r'gmax ?[1l] ?[@g]ellmax.c ?om'): 'gmax1@ellmax.com',
    re.compile(r"[ijlp']ee[vy]acation[©@a(&,P ]{1,3}g?mail.com"): 'jeevacation@gmail.com',
    'gyahoo.com': '@yahoo.com',
    # Signatures
    'Envoy& de': 'Envoyé de',
    'Envoye avec BlackBerry° d': 'Envoye avec BlackBerry® d',
    'from Samsung Mob.le': 'from Samsung Mobile',
    'gJeremyRubin': '@JeremyRubin',
    'Mail for i Phone': 'Mail for iPhone',
    'Sent from Mabfl': 'Sent from Mobile',  # NADIA_MARCINKO signature bad OCR
    'twitter glhsummers': 'twitter @lhsummers',
    re.compile(r'Blac[il]cBerry'): 'BlackBerry',
    'BlackBerry by AT &T': 'BlackBerry by AT&T',  # Must come after previous
    'BlackBerry from T- Mobile': 'BlackBerry from T-Mobile',
    re.compile(r"[cC]o-authored with i ?Phone auto-correct"): "Co-authored with iPhone auto-correct",
    re.compile(r"from my ['!()=]([Pp]hone)"): r'from my i\1',
    re.compile(r'from my BlackBerry[0°] wireless device'): 'from my BlackBerry® wireless device',
    re.compile(r'^INW$', re.MULTILINE): REDACTED,
    re.compile(r'Sent from one of my many test mobile devices while on the go and changing the world\s+:\s+so\s+my\s+apologies for any typos'): 'Sent from one of my many test mobile devices while on the go and changing the world : so my apologies for any typos',
    re.compile(r"twitter\.com[i/][lI]krauss[1lt]"): "twitter.com/lkrauss1",
    # links
    'classified-intelligence-\nmichael-flynn-trump': 'classified-intelligence-michael-flynn-trump',
    'on-accusers-rose-\nmcgowan/ ': 'on-accusers-rose-\nmcgowan/\n',
    'woody-allen-jeffrey-epsteins-\nsociety-friends-close-ranks/ ---': 'woody-allen-jeffrey-epsteins-society-friends-close_ranks/\n',
    ' https://www.theguardian.com/world/2017/may/29/close-friend-trump-thomas-barrack-\nalleged-tax-evasion-italy-sardinia?CMP=share btn fb': '\nhttps://www.theguardian.com/world/2017/may/29/close-friend-trump-thomas-barrack-alleged-tax-evasion-italy-sardinia?CMP=share_btn_fb',
    'search-for-secret-putin-\nfortune.html': 'search-for-secret-putin-fortune.html',
    re.compile(r"[h=][t=][t=][p=]://\s*"): 'http://',
    re.compile(r"([h=][t=][t=][op=][s=]|Imps )://\s*"): 'https://',
    re.compile(r'timestopics/people/t/landon jr thomas/inde\n?x\n?\.\n?h\n?tml'): 'timestopics/people/t/landon_jr_thomas/index.html',
    re.compile(r" http ?://www. ?dailymail. ?co ?.uk/news/article-\d+/Troub ?led-woman-history-drug-\n?us ?e-\n?.*html"): '\nhttp://www.dailymail.co.uk/news/article-3914012/Troubled-woman-history-drug-use-claimed-assaulted-Donald-Trump-Jeffrey-Epstein-sex-party-age-13-FABRICATED-story.html',
    re.compile(r"http.*steve-bannon-trump-tower-\n?interview-\n?trumps-\n?strategist-plots-\n?new-political-movement-948747"): "\nhttp://www.hollywoodreporter.com/news/steve-bannon-trump-tower-interview-trumps-strategist-plots-new-political-movement-948747",
    # Subject lines
    r'Priebus, used\nprivate email accounts for': 'Priebus, used private email accounts for',
    r"avoids testimony from alleged\nvictims": "avoids testimony from alleged victims",
    r"Subject; RE": "Subject: RE",
    re.compile(r"as Putin Mayhem\sTests\sPresident's\sGrip\son\sGOP"): "as Putin Mayhem Tests President's Grip on GOP",
    re.compile(r"deadline re Mr Bradley Edwards vs Mr\s*Jeffrey Epstein", re.I): "deadline re Mr Bradley Edwards vs Mr Jeffrey Epstein",
    re.compile(r"Following Plea That Implicated Trump -\s*https://www.npr.org/676040070", re.I): "Following Plea That Implicated Trump - https://www.npr.org/676040070",
    re.compile(r"for Attorney General -\s+Wikisource, the"): r"for Attorney General - Wikisource, the",
    re.compile(r"JUDGE SWEET\s+ALLOWING\s+STEVEN\s+HOFFENBERG\s+TO\s+TALK\s+WITH\s+THE\s+TOWERS\s+VICTIMS\s+TO\s+EXPLAIN\s+THE\s+VICTIMS\s+SUI\n?T\s+FILING\s+AGAINST\s+JEFF\s+EPSTEIN"): "JUDGE SWEET ALLOWING STEVEN HOFFENBERG TO TALK WITH THE TOWERS VICTIMS TO EXPLAIN THE VICTIMS SUIT FILING AGAINST JEFF EPSTEIN",
    re.compile(r"Lawyer for Susan Rice: Obama administration '?justifiably concerned' about sharing Intel with\s*Trump team -\s*POLITICO", re.I): "Lawyer for Susan Rice: Obama administration 'justifiably concerned' about sharing Intel with Trump team - POLITICO",
    re.compile(r"PATTERSON NEW\s+BOOK\s+TELLING\s+FEDS\s+COVER\s+UP\s+OF\s+BILLIONAIRE\s+JEFF\s+EPSTEIN\s+CHILD\s+RAPES\s+RELEASE\s+DATE\s+OCT\s+10\s+2016\s+STEVEN\s+HOFFENBERG\s+IS\s+ON\s+THE\s+BOOK\s+WRITING\s+TEAM\s*!!!!"): "PATTERSON NEW BOOK TELLING FEDS COVER UP OF BILLIONAIRE JEFF EPSTEIN CHILD RAPES RELEASE DATE OCT 10 2016 STEVEN HOFFENBERG IS ON THE BOOK WRITING TEAM !!!!",
    re.compile(r"PROCEEDINGS FOR THE ST THOMAS ATTACHMENT OF\s*ALL JEFF EPSTEIN ASSETS"): "PROCEEDINGS FOR THE ST THOMAS ATTACHMENT OF ALL JEFF EPSTEIN ASSETS",
    re.compile(r"Subject:\s*Fwd: Trending Now: Friends for three decades"): "Subject: Fwd: Trending Now: Friends for three decades",
    # Russian
    # Bocmpeceime
    re.compile(r'^B(TOpHHK|oc[xKm]pec\w+)', re.MULTILINE | re.IGNORECASE): 'Вторник',
    re.compile(r"^Cpe\w{2,},", re.MULTILINE | re.IGNORECASE): 'среда,',
    re.compile(r"^Cy66.rr?a", re.MULTILINE | re.IGNORECASE): 'суббота',
    re.compile(r"^flo\w{7,8}[HKhkw],", re.MULTILINE): 'понедельник,',
    re.compile(r"^TeMa:", re.MULTILINE | re.IGNORECASE): 'Тема:',
    re.compile(r"^KoMy:", re.MULTILINE | re.IGNORECASE): 'Кому:',
    re.compile(r"^Aara:", re.MULTILINE | re.IGNORECASE): 'Дата:',
    re.compile(r"^[O0]T:", re.MULTILINE | re.IGNORECASE): 'От:',
    # XML footers
    re.compile('<[iI] ?nteger>'): '<integer>',
    # Misc
    'AVG°': 'AVGO',
    'Saw Matt C with DTF at golf': 'Saw Matt C with DJT at golf',
    re.compile(r"[i. ]*Privileged[- ]*Redacted[i. ]*"): '<PRIVILEGED - REDACTED>',
    re.compile(r"SONY ?(Court|Judge|(, |/)NY)", re.IGNORECASE): r'SDNY \1',
}

METADATA_FIELDS = [
    'attachments',
    'attachment_file_ids',
    'is_junk_mail',
    'is_mailing_list',
    'extracted_recipients',
    'recipients',
    'sent_from_device',
]

DEBUG_PROPS = METADATA_FIELDS + [
    'attachment_file_ids',
    'is_persons_first_email',
    'is_word_count_worthy',
]


@dataclass
class Email(Communication):
    """
    Attributes:

        attached_docs (list[OtherFile]): any attachments that exist as `OtherFile` objects
        actual_text (str): Best effort at the text *actually* sent in this email excluding quoted replies and forwards
        derived_cfg (EmailCfg): EmailCfg that was built instead of coming from `CONFIGS_BY_ID`
        is_persons_first_email (bool): is this the first email we have for any of the participants (sender + recipients)
        sent_from_device (str, optional): "Sent from my iPhone" style signature (if it exists).
        signature_substitution_counts (dict[str, int]): Number of times a signature was replaced with
            <...snipped...> per name

        _header (EmailHeader): Header data extracted from the text (from/to/sent/subject etc).
        _line_merge_arguments (list[tuple[int] | tuple[int, int]]): preconfigured list of line merges that will fix up
            files from the HOUSE_OVERSIGHT_ collection in memory while leaving the source files untouched
        _was_split_up (bool, optional): True if this file Email was one of the big ones that was split into pieces
            and thus should generally be hidden / not shown
    """
    attached_docs: list[OtherFile] = field(default_factory=list)
    actual_text: str = field(init=False)
    derived_cfg: EmailCfg | None = None
    is_persons_first_email: bool = False
    sent_from_device: str | None = None
    signature_substitution_counts: dict[str, int] = field(default_factory=dict)  # defaultdict breaks asdict :(
    _header: EmailHeader | None = None
    _line_merge_arguments: list[tuple[int] | tuple[int, int]] = field(default_factory=list)
    _was_split_up: bool = False

    # Class variable logging how many headers we prettified while printing, kind of janky
    rewritten_header_ids: ClassVar[set[str]] = set([])

    def __post_init__(self):
        super().__post_init__()
        self.actual_text = self._extract_actual_text()
        self.sent_from_device = self._sent_from_device()

        # Scan for any identifiers we may have missed that could unredact this email
        for regex, contact in IDENTIFYING_REGEXES.items():
            if regex.search(self.text) and contact.name not in self.participants and self.file_id not in IDENTIFIER_FALSE_ALARMS:
                self._warn(f"Found known identifier for {contact.name} in email where they are not an identified participant")

    @property
    def attachment_file_ids(self) -> list[str]:
        """Strings in the Attachments: field in the header, split by semicolon."""
        return [a.file_id for a in self.attached_docs]

    @property
    def attachments(self) -> list[str]:
        """Strings in the Attachments: and Inline-Images: fields in the header, split by semicolon."""
        return self.header.all_attachments

    @property
    def char_range_to_display(self) -> CharRange | None:
        """Override superclass to decide how many chars we should limit the dislpay of this email to."""
        quote_cutoff = self._idx_of_nth_quoted_reply()  # Trim if there's many quoted replies
        includes_truncate_term = next((term for term in TRUNCATE_TERMS if term in self.text), None)
        num_chars: int | None = None

        if args.whole_file or self._config.truncate_at == NO_TRUNCATE:
            return None
        elif args.truncate:
            num_chars = args.truncate
        elif self._config.char_range:
            return self._config.char_range
        elif self.author in TRUNCATE_EMAILS_BY \
                or any([self.is_from_or_to(n) for n in TRUNCATE_EMAILS_FROM_OR_TO]) \
                or includes_truncate_term:
            num_chars = min(quote_cutoff or DEFAULT_TRUNCATE_TO, SHORT_TRUNCATE_TO)
        else:
            if quote_cutoff and quote_cutoff < DEFAULT_TRUNCATE_TO:
                trimmed_words = self.text[quote_cutoff:].split()

                # TODO this attempt to include <snipped> msgs in the truncated text kind of sucks
                if '<...snipped' in trimmed_words[:NUM_WORDS_IN_LAST_QUOTE]:
                    num_trailing_words = 0
                elif trimmed_words and trimmed_words[0] in ['From:', 'Sent:']:
                    num_trailing_words = NUM_WORDS_IN_LAST_QUOTE
                else:
                    num_trailing_words = NUM_WORDS_IN_LAST_QUOTE

                if trimmed_words:
                    last_quoted_text = ' '.join(trimmed_words[:num_trailing_words])
                    num_chars = quote_cutoff + len(last_quoted_text) + 1 # Give a hint of the next line
                else:
                    num_chars = quote_cutoff
            elif self.length > DEFAULT_TRUNCATE_TO:
                num_chars = DEFAULT_TRUNCATE_TO

            # Always print whole email for 1st email for actual people
            if num_chars and self.is_persons_first_email and self.is_word_count_worthy:
                self._log(f"Overriding cutoff {num_chars} for first email")
                num_chars = None

        log_args = {
            'num_chars': num_chars,
            'author_truncate': self.author in TRUNCATE_EMAILS_BY,
            'is_fwded_article': self.is_fwded_article,
            'is_quote_cutoff': quote_cutoff == num_chars,
            'includes_truncate_term': json.dumps(includes_truncate_term) if includes_truncate_term else None,
            'quote_cutoff': quote_cutoff,
            'is_persons_first_email': self.is_persons_first_email,
        }

        log_args_str = ', '.join([f"{k}={v}" for k, v in log_args.items() if v])
        self._debug_log(f"Truncate determination: {log_args_str}")
        return None if num_chars is None else (0, num_chars)

    @property
    def config(self) -> EmailCfg | None:
        """Configured timestamp, if any."""
        if self.file_info.is_local_extract_file:
            this_file_cfg = cast(EmailCfg, CONFIGS_BY_ID.get(self.file_info.file_id))

            # Merge config for file this was extracted from into self.derived_cfg
            if not self.derived_cfg and (extracted_from_cfg := CONFIGS_BY_ID.get(self.file_info.url_slug)):
                self.derived_cfg = this_file_cfg or EmailCfg(id=self.file_id)

                # Add "appears in [SOURCE]" pfx to description for docs extract ed from others (e.g. huge Dilorio emails)
                if (extracted_from_description := extracted_from_cfg.complete_description):
                    self.derived_cfg.note = f"{APPEARS_IN} {extracted_from_description}"

                for prop in DERIVED_CFG_PROPS_TO_COPY:
                    derived_cfg_val = getattr(self.derived_cfg, prop)

                    if is_bool_prop(prop) and derived_cfg_val is not None:
                        continue  # Don't overwrite booleans

                    extracted_cfg_val = getattr(extracted_from_cfg, prop)
                    setattr(self.derived_cfg, prop, derived_cfg_val or extracted_cfg_val)

                self._log(f"Constructed synthetic config: {self.derived_cfg}")

            return self.derived_cfg or this_file_cfg
        else:
            return super().config

    @property
    def _config(self) -> EmailCfg:
        # TODO: annoying to unnecessarily override superclass just to get python to understanding the types
        return self.config or self.dummy_cfg()

    @property
    def display_text(self) -> str:
        """Config overrides what text should be displayed."""
        return str(self.email_parts)
        return collapse_newlines(self._config.display_text or self.text)

    @property
    def header(self) -> EmailHeader:
        self._header = self._header or self.extract_header()
        return self._header

    @property
    def email_parts(self) -> EmailParts:
        """Separate header chars from the rest of the email text."""
        num_header_lines = self.header.num_header_rows

        if self.header.should_rewrite_header:
            header = self.header.rewrite_header()
            lines = []

            # TODO: Emails w/configured 'actual_text' are particularly broken; need to shuffle some lines
            if (actual_text := self._config.actual_text) is not None:
                lines.extend([cast(str, actual_text), '\n'])
                num_header_lines += 1

            lines.extend(self.lines[num_header_lines:])
            body = _add_line_breaks('\n'.join(lines))
        else:
            header = '\n'.join(self.lines[0:num_header_lines])
            body = '\n'.join(self.lines[num_header_lines:])

        return EmailParts(header, body)

    @property
    def html_margin_bottom(self) -> str:
        """Overloaded in `Email` for case of emails with attachments."""
        if self.attached_docs:
            return '6px'
        else:
            return super().html_margin_bottom

    @property
    def info(self) -> list[Text]:
        """Overloads superclass to avoid returning config_description because that's now in the Panel title."""
        if site_config.email_info_in_subtitle:
            return [self.subheader]
        else:
            return super().info

    @property
    def is_fwded_article(self) -> bool:
        """True if this email is just a forward of an article from WSJ or whatever."""
        if self._config.is_fwded_article is not None:
            return self._config.is_fwded_article
        elif self._config.fwded_text_after:
            return (len(self.actual_text) < 100)
        else:
            return False

    @property
    def is_interesting(self) -> bool | None:
        """Junk emails are not interesting, configured value takes precedence, fallback to EMAILERS_OF_INTEREST check."""
        if self.is_mailing_list:
            return False
        elif (is_interesting := super().is_interesting) is not None:
            return is_interesting
        elif self.participants.intersection(EMAILERS_OF_INTEREST_SET):
            return True

    @property
    def is_junk_mail(self) -> bool:
        return self.author in JUNK_EMAILERS

    @property
    def is_mailing_list(self) -> bool:
        return self.author in MAILING_LISTS or self.is_junk_mail

    @property
    def is_word_count_worthy(self) -> bool:
        """True if this file should be included in word counts."""
        return not (self.is_fwded_article or self.is_mailing_list or self.is_duplicate)

    @property
    def metadata(self) -> Metadata:
        metadata = {**super().metadata, **self.truthy_props(METADATA_FIELDS)}

        if not self.header.is_empty:
            metadata['header'] = self.header.as_dict()

        if self.attached_docs:
            metadata['attachment_file_ids'] = [f.file_id for f in self.attached_docs]

        return metadata

    @property
    def prettified_txt(self) -> Text:
        """Overrides superclass. Cleaned up / formatted Text ready to be displayed."""
        if self._config.char_range and self._config.char_range[0] > 0:
            if self._config.char_range[0] < self.email_parts.header_len:
                self._warn(f"The excerpt appears to start in the email header which will may in duplicate header chars")

            # always show the email header even if only a configured excerpt is being displayed
            return self.email_parts.header_txt.append('\n\n').append(super().prettified_txt)
        else:
            return super().prettified_txt

    @property
    def recipients_str(self) -> str:
        return ';'.join([str(r) for r in self.recipients])

    @property
    def subheader(self) -> Text:
        """String describing this email including author, recipients, and timestamp."""
        author_txt = self.author_txt

        if self._config.author_uncertain:
            author_txt += Text(f" {QUESTION_MARKS}", style=self.author_style)

        prefix = 'fwded article' if self.is_fwded_article else 'email'
        return site_config.email_subheader(prefix, author_txt, self.recipients_txt(), self.timestamp)

    @property
    def subject(self) -> str:
        """String in the Subject: header line."""
        return self._config.subject or self.header.subject or ''

    @property
    def uninteresting_txt(self) -> Text | None:
        """Text to print for uninteresting files."""
        if (uninteresting_txt := super().uninteresting_txt):
            if self.subject:
                uninteresting_txt.append(f' ("{self.subject}")', style='light_yellow3')

            return uninteresting_txt

    @property
    def _summary(self) -> Text:
        """Append the recipients to Document._summary() and close the bracket."""
        txt = self._summary_with_author

        if self.recipients:
            txt.append(', ').append(styled_key_value('recipients', self.recipients_txt()))

        return txt.append(CLOSE_PROPERTIES_CHAR)

    def entity_scan(self, exclude: EntityScanArg = None, include: EntityScanArg = None) -> list[Entity]:
        """Overrides superclass to append names from email attachments."""
        attachment_entities = flatten([ad.entities for ad in self.attached_docs])
        include = Entity.coerce_entity_names(attachment_entities) + Entity.coerce_entity_names(include)
        return super().entity_scan(exclude, include)

    def extract_author(self) -> Name:
        """Overloads superclass method, called at instantiation time."""
        if self.header.author:
            authors = without_falsey(extract_emailer_names(self.header.author))
            return authors[0] if authors else None

    def extract_header(self) -> EmailHeader:
        """Extract an `EmailHeader` from the OCR text."""
        header_match = EMAIL_SIMPLE_HEADER_REGEX.search(self.text)

        if header_match:
            header = EmailHeader.from_header_lines(header_match.group(0))

            # DOJ file OCR text is broken in a less consistent way than the HOUSE_OVERSIGHT files
            if header.is_empty and not self.file_info.is_doj_file:
                header.repair_empty_header(self.lines)
        else:
            self._log_top_lines(msg='No email header found!', level=logging.INFO if self.config else logging.WARNING)
            header = EmailHeader(field_names=[])

        logger.debug(f"{self.file_id} extracted header\n\n{header}\n")
        return header

    def extract_recipients(self) -> list[Name]:
        """Scan the To:, BCC: and CC: fields for known names, falling back to raw strings if no names identified."""
        recipients = uniquify(flatten([extract_emailer_names(r) for r in self.header.recipients]))

        # Assume mailing list emails are to Epstein
        if self.author in BCC_LISTS and (self.is_note_to_self(recipients) or not recipients):
            recipients: list[Name] = [JEFFREY_EPSTEIN]

        # Remove self CCs but preserve self emails
        if self.author and self.author in recipients and not self.is_note_to_self(recipients):
            self._log(f"Removing email to self for {self.author}")
            recipients = [r for r in recipients if r != self.author]

        # Add None to recipients if there's an empty From: or To: header
        if self.header.is_to_redacted and not self.has_unknown_recipient:
            # TODO: SEC is filled in for Dilorio's split up emails after Email is fully instantiated
            if self.author != CHRISTOPHER_DILORIO:
                self._log(f"Appending {None} to recipient list because the To: field is empty")
                recipients.append(None)

        return sort_names(recipients)

    def extract_timestamp(self) -> datetime:
        """Find the time this email was sent by attempting to parse the headers."""
        if self.header.sent_at and (timestamp := _parse_email_timestamp(self.header.sent_at)):
            return timestamp

        searchable_lines = self.lines[0:MAX_NUM_HEADER_LINES]
        searchable_text = '\n'.join(searchable_lines)

        if (date_match := DATE_HEADER_REGEX.search(searchable_text)):
            if (timestamp := _parse_email_timestamp(date_match.group(1))):
                return timestamp

        logger.debug(f"Failed to find timestamp, falling back to parsing {MAX_NUM_HEADER_LINES} lines...")

        for line in searchable_lines:
            if not TIMESTAMP_LINE_REGEX.search(line):
                continue

            if (timestamp := _parse_email_timestamp(line)):
                logger.debug(f"Fell back to timestamp {timestamp} in line '{line}'...")
                return timestamp

        no_timestamp_msg = f"No timestamp found in '{self.file_path.name}'"

        if self._config.duplicate_of_id:
            logger.warning(f"{no_timestamp_msg} but timestamp should be copied from {self._config.duplicate_of_id}")
        else:
            logger.error(f"{no_timestamp_msg}, top lines:\n" + '\n'.join(self.lines[0:MAX_NUM_HEADER_LINES + 10]))

        return FALLBACK_TIMESTAMP

    def file_display(self, align: JustifyMethod | None = None) -> FileDisplay:
        """Allows for proper right vs. left justify."""
        return FileDisplay(
            body_panel=self._body_as_table(self.prettified_txt, self._config.note_txt),
            file_info=self.file_id_panel,
            indent=site_config.info_indent,
            justify=align,
            margin_bottom=self.html_margin_bottom,
            subheaders=self.info,
        )

    def is_from_or_to(self, name: str) -> bool:
        """True if `name` is either the author or one of the recipients."""
        return name in self.participants

    def is_note_to_self(self, recipients: list[Name] | None = None) -> bool:
        return (recipients if recipients is not None else self.recipients) == [self.author]

    def recipients_txt(self, max_full_names: int = 2) -> Text:
        """Comma separated colored names (last name only if more than `max_full_names` recipients)."""
        recipients = [r or UNKNOWN for r in self.recipients] if len(self.recipients) > 0 else [UNKNOWN]

        names = [
            Text(r if len(recipients) <= max_full_names else extract_last_name(r), get_style_for_name(r)) + \
                (Text(f" {QUESTION_MARKS}", get_style_for_name(r)) if self._config.recipient_uncertain else Text(''))
            for r in recipients
        ]

        return join_texts(names, join=', ')

    def to_html(self) -> str:
        html = super().to_html()

        if (attachments_table := self._attached_docs_table()):
            indent_props = {'margin-left': to_em(site_config.attachment_indent)}
            html += table_to_html(attachments_table, indent_props)

        return html

    def _attached_docs_table(self) -> Table | None:
        if not self.attached_docs:
            return None

        attachments_table_title = f"| Email Attachments for {self.file_info.url_slug}:" # ╏┇┣

        if (doc := self.attached_docs[0])._config.show_full_panel:
            if len(self.attached_docs) > 1:
                raise ValueError(f"Can't show more than one panelized attachment for {self}!")

            table = Table(title=attachments_table_title, title_justify='left')
            table.add_column(doc._config.note)
            table.add_row(highlighter(Text(self.attached_docs[0].text, EXCERPT_STYLE)))
            return table
        else:
            return OtherFile.files_preview_table(self.attached_docs, title=attachments_table_title)

    def _body_as_panel(self, text: str | Text, description: Text | None = None) -> Panel:
        """Renders the info info text in the panel's bottom border."""
        return Panel(
            text,
            border_style=self.border_style,
            expand=False,
            title=Text(' ').join(description.split(' ')) if description else None,  # split then join makes rich color subtitle correctly
            title_align='right',
        )

    def _body_as_table(self, text: str | Text, description: Text | None = None) -> Table:
        """Renders the info text as a top row in a table-ish view."""
        panel = Table(
            border_style=self.border_style,
            box=box.ROUNDED,
            header_style='on gray11',
            show_header=bool(description)
        )

        if description and site_config.email_info_in_subtitle:
            description = Text('', justify='right').append(description)

        panel.add_column(description or '')
        panel.add_row(text)
        return panel

    def _debug_props(self) -> DebugDict:
        props = super()._debug_props()
        local_props = self.truthy_props(DEBUG_PROPS)
        local_props['extracted_recipients'] = self.extracted_recipients

        if not self.header.is_empty:
            local_props['header'] = self.header.as_dict()
        if self.is_note_to_self():
            local_props['is_note_to_self'] = self.is_note_to_self()

        props.update(prefix_keys(self._debug_prefix, local_props))
        return props

    def _extract_actual_text(self) -> str:
        """The text that comes before likely quoted replies and forwards etc."""
        if self._config.actual_text is not None:
            return self._config.actual_text

        text = '\n'.join(self.text.split('\n')[self.header.num_header_rows:]).strip()

        if self._config.fwded_text_after:
            return text.split(self._config.fwded_text_after)[0].strip()
        elif self.header.num_header_rows == 0:
            return self.text

        self._log_top_lines(20, "Raw text:", logging.DEBUG)
        self._log(f"With {self.header.num_header_rows} header lines removed:\n{text[0:500]}\n\n", logging.DEBUG)
        reply_text_match = REPLY_TEXT_REGEX.search(text)

        if reply_text_match:
            actual_num_chars = len(reply_text_match.group(1))
            actual_text_pct = f"{(100 * float(actual_num_chars) / len(text)):.1f}%"
            logger.debug(f"'{self.file_id}': actual_text() reply_text_match is {actual_num_chars:,} chars ({actual_text_pct} of {len(text):,})")
            text = reply_text_match.group(1)

        # If all else fails look for lines like 'From: blah', 'Subject: blah', and split on that.
        for field_name in REPLY_SPLITTERS:
            field_string = f'\n{field_name}'

            if field_string not in text:
                continue

            pre_from_text = text.split(field_string)[0]
            actual_num_chars = len(pre_from_text)
            actual_text_pct = f"{(100 * float(actual_num_chars) / len(text)):.1f}%"
            logger.debug(f"'{self.file_id}': actual_text() fwd_text_match is {actual_num_chars:,} chars ({actual_text_pct} of {len(text):,})")
            text = pre_from_text
            break

        return text.strip()

    def _idx_of_nth_quoted_reply(self, n: int = MAX_QUOTED_REPLIES) -> int | None:
        """Get position of the nth 'On June 12th, 1985 [SOMEONE] wrote:' style line in self.text."""
        header_offset = len(self.header.header_chars)
        text = self.text[header_offset:]

        for i, match in enumerate(QUOTED_REPLY_LINE_REGEX.finditer(text)):
            if i >= n:
                return match.end() + header_offset - 1

    def _remove_bad_lines(self) -> None:
        """Get rid of crufty lines matching `BAD_LINE_REGEX`"""
        self._set_text(lines=[line for line in self.lines if not BAD_LINE_REGEX.match(line)])

    def _repair(self) -> None:
        """Repair particularly janky files. Note that OCR_REPAIRS are applied *after* other line adjustments."""
        # for line in self.lines[0:NUM_LINES_TO_REPAIR_HEADERS]:
        #     if HEADER_REPAIR_REGEX.match(line):
        #         self._warn(f'reparable header line: {quote(line)}')

        super()._repair()

        # Apply custom repairs for DOJ files
        if self.file_info.is_doj_file:
            new_text = DojFile._remove_bad_lines(strip_pdfalyzer_panels(self.text))
            self._set_text(text=self.repair_ocr_text(DOJ_EMAIL_OCR_REPAIRS, new_text))

        if BAD_FIRST_LINE_REGEX.match(self.lines[0]):
            self._set_text(lines=self.lines[1:])

        self._remove_bad_lines()
        self.__bespoke_repair_house_oversight_emails()
        self._set_text(text=self.repair_ocr_text(OCR_REPAIRS, self.text))

        if self.file_id in SINGLE_EMAIL_OCR_REPAIRS:
            self._debug_log('applying bespoke OCR repairs')
            self._set_text(text=self.repair_ocr_text(SINGLE_EMAIL_OCR_REPAIRS[self.file_id], self.text))

        self._repair_links_and_quoted_subjects()
        self._format_newlines_and_snip_signatures()

    def _repair_links_and_quoted_subjects(self) -> None:
        """Repair links that the OCR has broken into multiple lines as well as 'Subject:' lines."""
        subject_line = next((line for line in self.lines if line.startswith('Subject:')), None) or ''
        subject = subject_line.split(':')[1].strip() if subject_line else ''
        lines = self.lines
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if LINK_LINE_REGEX.search(line):
                while i < (len(lines) - 1) \
                        and not (lines[i + 1].startswith('htt') or lines[i + 1].startswith('www') or lines[i + 1].endswith('com')) \
                        and (lines[i + 1].endswith('/') \
                            or any(s in lines[i + 1] for s in URL_SIGNIFIERS) \
                            or LINK_LINE2_REGEX.match(lines[i + 1])):
                    logger.debug(f"{self.filename}: Joining link lines\n   1. {line}\n   2. {lines[i + 1]}\n")
                    line += lines[i + 1]
                    i += 1

                line = line if '[' in line or ']' in line else line.replace(' ', '')
            elif ' http' in line and line.endswith('html'):
                pre_link, post_link = line.split(' http', 1)
                line = f"{pre_link} http{post_link.replace(' ', '')}"
            elif line.startswith('Subject:') and i < (len(lines) - 2) and len(line) >= 40:
                next_line = lines[i + 1]
                next_next = lines[i + 2]

                if len(next_line) <= 1 or any([cont in next_line for cont in BAD_SUBJECT_CONTINUATIONS]):
                    pass
                elif (subject.endswith(next_line) and next_line != subject) \
                        or (HEADER_FIELD_COLON_REGEX.search(next_next) and not HEADER_FIELD_COLON_REGEX.search(next_line)):
                    self._log(f"Fixing broken subject line\n  line: '{line}'\n    next: '{next_line}'\n    next: '{next_next}'\nsubject='{subject}'\n")
                    line += f" {next_line}"
                    i += 1

            new_lines.append(line)
            i += 1

        self._debug_log(f"----after line repair---\n" + '\n'.join(new_lines[0:20]) + "\n---")
        self._set_text(lines=new_lines)

    def _sent_from_device(self) -> str | None:
        """Find any 'Sent from my iPhone' style signature line if it exist in the 'actual_text'."""
        if (sent_from_match := SENT_FROM_REGEX.search(self.actual_text)):
            sent_from = sent_from_match.group(0).strip()

            if sent_from.startswith('Typos, misspellings courtesy of iPhone'):  # special handling for linda stone periods
                return sent_from.removesuffix('.')
            elif sent_from.startswith('sent'):
                return capitalize_first(sent_from)
            else:
                return sent_from

    def _format_newlines_and_snip_signatures(self) -> None:
        """Add newlines before quoted replies, snip signatures and XML, etc.."""
        # Insert line breaks now unless header is broken, in which case we'll do it later after fixing header
        # self._debug_log(f"text before _add_line_breaks:\n\n{self.text}\n---")
        text = self.text if self.header.was_initially_empty else _add_line_breaks(self.text)
        text = REPLY_REGEX.sub(r'\n\1', text)  # Newlines between quoted replies
        text = FORWARDED_TOO_MUCH_SPACE_REGEX.sub(r'\1\n', text)
        # self._debug_log(f"text after _add_line_breaks:\n\n{text}\n---")

        for name, signature_regex in EMAIL_SIGNATURE_REGEXES.items():
            signature_replacement = f'<...snipped {name.lower()} email signature...>'
            text, num_replaced = signature_regex.subn(signature_replacement, text)
            self.signature_substitution_counts[name] = self.signature_substitution_counts.get(name, 0)
            self.signature_substitution_counts[name] += num_replaced

        # Remove XML cruft in some files
        text, num_plists_stripped = XML_PLIST_REGEX.subn(XML_STRIPPED_MSG, text)

        if num_plists_stripped:
            self._log(f"Replaced {num_plists_stripped} XML plists...")

        self._set_text(text=collapse_newlines(text).strip())
        self._remove_bad_lines()  # TODO: we're currently calling this twice to handle lines with HTML garbage that turn into something matching BAD_LINE_REGEX

    def __bespoke_repair_house_oversight_emails(self) -> None:
        """Apply destructive repairs to the underyling text programmtically because we don't want to edit the underlying file."""
        old_text = self.text

        if self.file_id in LINE_REPAIR_MERGES:
            for merge_args in LINE_REPAIR_MERGES[self.file_id]:
                self.__merge_lines(*merge_args)

        if self.file_id in ['025233']:
            self.lines[4] = f"Attachments: {self.lines[4]}"
            self._set_text(lines=self.lines)
        elif self.file_id == '029977':
            self._set_text(text=self.text.replace('Sent 9/28/2012 2:41:02 PM', 'Sent: 9/28/2012 2:41:02 PM'))
        elif self.file_id == '025041':
            self.__remove_line(4)
            self.__remove_line(4)
        elif self.file_id == '029692':
            self.__remove_line(3)

        if old_text != self.text:
            self._log(f"Modified text, old:\n\n" + '\n'.join(old_text.split('\n')[0:12]) + '\n')
            self._log_top_lines(12, 'Result of modifications')

    def __merge_lines(self, idx1: int, idx2: int | None = None) -> None:
        """Combine lines numbered 'idx' and 'idx2' into a single line (idx2 defaults to idx + 1)."""
        if idx2 is None:
            self._line_merge_arguments.append((idx1,))
            idx2 = idx1 + 1
        else:
            self._line_merge_arguments.append((idx1, idx2))

        if idx2 < idx1:
            lines = self.lines[0:idx2] + self.lines[idx2 + 1:idx1] + [self.lines[idx1] + ' ' + self.lines[idx2]] + self.lines[idx1 + 1:]
        elif idx2 == idx1:
            raise RuntimeError(f"idx2 ({idx2}) must be greater or less than idx ({idx1})")
        else:
            lines = self.lines[0:idx1]

            if idx2 == (idx1 + 1):
                lines += [self.lines[idx1] + ' ' + self.lines[idx1 + 1]] + self.lines[idx1 + 2:]
            else:
                lines += [self.lines[idx1] + ' ' + self.lines[idx2]] + self.lines[idx1 + 1:idx2] + self.lines[idx2 + 1:]

        self._set_text(lines=lines)

    def __remove_line(self, idx: int) -> None:
        """Remove a line from `self.lines`."""
        num_lines = idx * 2
        self._log_top_lines(num_lines, msg=f'before removal of line {idx}')
        del self.lines[idx]
        self._set_text(lines=self.lines)
        self._log_top_lines(num_lines, msg=f'after removal of line {idx}')

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        prettified_txt = self.prettified_txt
        max_line_len = max(*[len(line) for line in prettified_txt.split('\n')])
        note_txt = None

        if self._config.note_txt and site_config.email_info_in_subtitle:
            max_line_len = max(max_line_len, len(self._config.note_txt.plain))
            note_txt = Text('').append(self._config.note_txt)
            note_txt.justify = 'right'

        if args.panelize_emails:
            body = self._body_as_panel(prettified_txt, note_txt)
        else:
            body = self._body_as_table(prettified_txt, note_txt)

        yield self.rich_header()
        body_bottom_padding = 0 if self.attached_docs else 1
        yield Padding(body, (0, 0, body_bottom_padding, site_config.other_files_table_indent))

        if (attachments_table := self._attached_docs_table()):
            yield Padding(attachments_table, (0, 0, 1, site_config.attachment_indent))

    @classmethod
    def dummy_cfg(cls) -> EmailCfg:
        return EmailCfg(id='DUMMY')

    @staticmethod
    def build_emails_table(emails: list['Email'], name: Name = '', title: str = '', show_length: bool = False, **kwargs) -> Table:
        """Turn a list of `Email` objects into a `Table` with sender, recipient, and subject line."""
        if title and name:
            raise ValueError(f"Can't provide both 'author' and 'title' args")
        elif name == '' and title == '':
            raise ValueError(f"Must provide either 'author' or 'title' arg")

        author_style = get_style_for_name(name, allow_bold=False)
        link_style = author_style if name else ARCHIVE_LINK_COLOR
        min_width = len(name or UNKNOWN)
        max_width = max(20, min_width)

        columns = [
            {'name': 'Sent At', 'justify': 'left', 'style': TIMESTAMP_DIM},
            {'name': 'From', 'justify': 'left', 'min_width': min_width, 'max_width': max_width},
            {'name': 'To', 'justify': 'left', 'min_width': min_width, 'max_width': max_width + 2},
            {'name': 'Length', 'justify': 'right', 'style': 'wheat4'},
            {'name': 'Subject', 'justify': 'left', 'min_width': 35, 'style': 'honeydew2'},
        ]

        table = build_table(
            title or None,
            cols=[col for col in columns if show_length or col['name'] not in ['Length']],
            border_style=DEFAULT_TABLE_KWARGS['border_style'] if title else author_style,
            header_style="bold",
            highlight=True,
            **kwargs
        )

        for email in emails:
            fields = [
                link_text_obj(email.file_info.external_url, email.timestamp_without_seconds, style=link_style),
                email.author_txt,
                email.recipients_txt(max_full_names=1),
                f"{email.length}",
                email.subject,
            ]

            if not show_length:
                del fields[3]

            table.add_row(*fields)

        return table


def _add_line_breaks(email_text: str) -> str:
    text = EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX.sub(r'\n\1\n', email_text).strip()
    # logger.debug(f"text after EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX _add_line_breaks()\n---\n{text}\n---")
    return FORWARDED_TOO_MUCH_SPACE_REGEX.sub(r'\1\n', text)


# TODO: this might be obsolete bc of usage of datutil or similar
def _parse_email_timestamp(timestamp_str: str) -> None | datetime:
    try:
        if (american_date_match := AMERICAN_TIME_REGEX.search(timestamp_str)):
            timestamp_str = american_date_match.group(1)
        else:
            timestamp_str = timestamp_str.replace('(GMT-05:00)', 'EST')
            timestamp_str = BAD_TIMEZONE_REGEX.sub(' ', timestamp_str).strip()

        timestamp = parse(timestamp_str, fuzzy=True, tzinfos=TIMEZONE_INFO)
        logger.debug(f'Parsed timestamp "%s" from string "%s"', timestamp, timestamp_str)
        return coerce_utc(timestamp)
    except Exception as e:
        logger.debug(f'Failed to parse "{timestamp_str}" to timestamp!')
        return None
