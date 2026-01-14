import json
import logging
import re
from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import ClassVar, cast

from dateutil.parser import parse
from rich.console import Console, ConsoleOptions, RenderResult
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from epstein_files.documents.communication import Communication
from epstein_files.documents.document import CLOSE_PROPERTIES_CHAR, INFO_INDENT
from epstein_files.documents.emails.email_header import (BAD_EMAILER_REGEX, EMAIL_SIMPLE_HEADER_REGEX,
     EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX, FIELD_NAMES, TIME_REGEX, EmailHeader)
from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.constants import *
from epstein_files.util.data import (TIMEZONE_INFO, collapse_newlines, escape_single_quotes,
     flatten, listify, remove_timezone, uniquify)
from epstein_files.util.doc_cfg import EmailCfg, Metadata
from epstein_files.util.file_helper import extract_file_id, file_stem_for_id
from epstein_files.util.highlighted_group import JUNK_EMAILERS, get_style_for_name
from epstein_files.util.logging import logger
from epstein_files.util.rich import *

BAD_FIRST_LINE_REGEX = re.compile(r'^(>>|Grant_Smith066474"eMailContent.htm|LOVE & KISSES)$')
BAD_LINE_REGEX = re.compile(r'^(>;?|\d{1,2}|PAGE INTENTIONALLY LEFT BLANK|Classification: External Communication|Importance:?\s*High|[iI,•]|i (_ )?i|, [-,]|L\._)$')
DETECT_EMAIL_REGEX = re.compile(r'^(.*\n){0,2}From:')
LINK_LINE_REGEX = re.compile(f"^>? ?htt")
LINK_LINE2_REGEX = re.compile(r"^[-\w.%&=/]{5,}$")
QUOTED_REPLY_LINE_REGEX = re.compile(r'(\nFrom:(.*)|wrote:)\n', re.IGNORECASE)
REPLY_TEXT_REGEX = re.compile(rf"^(.*?){REPLY_LINE_PATTERN}", re.DOTALL | re.IGNORECASE | re.MULTILINE)

BAD_TIMEZONE_REGEX = re.compile(fr'\((UTC|GMT\+\d\d:\d\d)\)|{REDACTED}')
DATE_HEADER_REGEX = re.compile(r'(?:Date|Sent):? +(?!by|from|to|via)([^\n]{6,})\n')
TIMESTAMP_LINE_REGEX = re.compile(r"\d+:\d+")
LOCAL_EXTRACT_REGEX = re.compile(r"_\d$")

SUPPRESS_LOGS_FOR_AUTHORS = ['Undisclosed recipients:', 'undisclosed-recipients:', 'Multiple Senders Multiple Senders']
REWRITTEN_HEADER_MSG = "(janky OCR header fields were prettified, check source if something seems off)"
URL_SIGNIFIERS = ['amp?', 'cd=', 'click', 'ft=', 'gclid', 'htm', 'keywords=', 'module=', 'mpweb', 'nlid=', 'ref=', 'smid=', 'usg=', 'utm']
APPEARS_IN = 'appears in'
MAX_CHARS_TO_PRINT = 4000
MAX_NUM_HEADER_LINES = 14
MAX_QUOTED_REPLIES = 2

REPLY_SPLITTERS = [f"{field}:" for field in FIELD_NAMES] + [
    '********************************',
    'Begin forwarded message',
]

OCR_REPAIRS: dict[str | re.Pattern, str] = {
    re.compile(r'grnail\.com'): 'gmail.com',
    'Newsmax. corn': 'Newsmax.com',
    re.compile(r"^(From|To)(: )?[_1.]{5,}", re.MULTILINE): rf"\1: {REDACTED}",  # Redacted email addresses
    # These 3 must come in this order!
    re.compile(r'([/vkT]|Ai|li|(I|7)v)rote:'): 'wrote:',
    re.compile(r"([<>.=_HIM][<>.=_HIM14]{5,}[<>.=_HIM]|MOMMINNEMUMMIN) *(wrote:?)?"): rf"{REDACTED} \2",
    re.compile(r"([,<>_]|AM|PM)\n(>)? ?wrote:?"): r'\1\2 wrote:',
    # Names / email addresses
    'Alireza lttihadieh': ALIREZA_ITTIHADIEH,
    'Miroslav Laj6ak': MIROSLAV_LAJCAK,
    'Ross G°w': ROSS_GOW,
    'Torn Pritzker': TOM_PRITZKER,
    re.compile(r' Banno(r]?|\b)'): ' Bannon',
    re.compile(r'gmax ?[1l] ?[@g]ellmax.c ?om'): 'gmax1@ellmax.com',
    re.compile(r"[ijlp']ee[vy]acation[©@a(&,P ]{1,3}g?mail.com"): 'jeevacation@gmail.com',
    # Signatures
    'BlackBerry by AT &T': 'BlackBerry by AT&T',
    'BlackBerry from T- Mobile': 'BlackBerry from T-Mobile',
    'Envoy& de': 'Envoyé de',
    "from my 'Phone": 'from my iPhone',
    'from Samsung Mob.le': 'from Samsung Mobile',
    'gJeremyRubin': '@JeremyRubin',
    'Sent from Mabfl': 'Sent from Mobile',  # NADIA_MARCINKO signature bad OCR
    'twitter glhsummers': 'twitter @lhsummers',
    re.compile(r"[cC]o-authored with i ?Phone auto-correct"): "Co-authored with iPhone auto-correct",
    re.compile(r"twitter\.com[i/][lI]krauss[1lt]"): "twitter.com/lkrauss1",
    re.compile(r'from my BlackBerry[0°] wireless device'): 'from my BlackBerry® wireless device',
    re.compile(r'^INW$', re.MULTILINE): REDACTED,
    # links
    'Imps ://': 'https://',
    re.compile(r'timestopics/people/t/landon jr thomas/inde\n?x\n?\.\n?h\n?tml'): 'timestopics/people/t/landon_jr_thomas/index.html',
    # Subject lines
    "Arrested in\nInauguration Day Riot": "Arrested in Inauguration Day Riot",
    "as Putin Mayhem Tests President's Grip\non GOP": "as Putin Mayhem Tests President's Grip on GOP",
    "avoids testimony from alleged\nvictims": "avoids testimony from alleged victims",
    "but\nwatchdogs say probe is tainted": "watchdogs say probe is tainted",
    "Christmas comes\nearly for most of macro": "Christmas comes early for most of macro",            # 023717
    "but majority still made good\nmoney because": "but majority still made good money because",      # 023717
    "COVER UP SEX ABUSE CRIMES\nBY THE WHITE HOUSE": "COVER UP SEX ABUSE CRIMES BY THE WHITE HOUSE",
    'Priebus, used\nprivate email accounts for': 'Priebus, used private email accounts for',
    "War on the Investigations\nEncircling Him": "War on the Investigations Encircling Him",
    re.compile(r"deadline re Mr Bradley Edwards vs Mr\s*Jeffrey Epstein", re.I): "deadline re Mr Bradley Edwards vs Mr Jeffrey Epstein",
    re.compile(r"Following Plea That Implicated Trump -\s*https://www.npr.org/676040070", re.I): "Following Plea That Implicated Trump - https://www.npr.org/676040070",
    re.compile(r"for Attorney General -\s+Wikisource, the"): r"for Attorney General - Wikisource, the",
    re.compile(r"JUDGE SWEET\s+ALLOWING\s+STEVEN\s+HOFFENBERG\s+TO\s+TALK\s+WITH\s+THE\s+TOWERS\s+VICTIMS\s+TO\s+EXPLAIN\s+THE\s+VICTIMS\s+SUI\n?T\s+FILING\s+AGAINST\s+JEFF\s+EPSTEIN"): "JUDGE SWEET ALLOWING STEVEN HOFFENBERG TO TALK WITH THE TOWERS VICTIMS TO EXPLAIN THE VICTIMS SUIT FILING AGAINST JEFF EPSTEIN",
    re.compile(r"Lawyer for Susan Rice: Obama administration '?justifiably concerned' about sharing Intel with\s*Trump team -\s*POLITICO", re.I): "Lawyer for Susan Rice: Obama administration 'justifiably concerned' about sharing Intel with Trump team - POLITICO",
    re.compile(r"PATTERSON NEW\s+BOOK\s+TELLING\s+FEDS\s+COVER\s+UP\s+OF\s+BILLIONAIRE\s+JEFF\s+EPSTEIN\s+CHILD\s+RAPES\s+RELEASE\s+DATE\s+OCT\s+10\s+2016\s+STEVEN\s+HOFFENBERG\s+IS\s+ON\s+THE\s+BOOK\s+WRITING\s+TEAM\s*!!!!"): "PATTERSON NEW BOOK TELLING FEDS COVER UP OF BILLIONAIRE JEFF EPSTEIN CHILD RAPES RELEASE DATE OCT 10 2016 STEVEN HOFFENBERG IS ON THE BOOK WRITING TEAM !!!!",
    re.compile(r"PROCEEDINGS FOR THE ST THOMAS ATTACHMENT OF\s*ALL JEFF EPSTEIN ASSETS"): "PROCEEDINGS FOR THE ST THOMAS ATTACHMENT OF ALL JEFF EPSTEIN ASSETS",
    re.compile(r"Subject:\s*Fwd: Trending Now: Friends for three decades"): "Subject: Fwd: Trending Now: Friends for three decades",
    # Misc
    'AVG°': 'AVGO',
}

EMAIL_SIGNATURE_REGEXES = {
    ARIANE_DE_ROTHSCHILD: re.compile(r"Ensemble.*\nCe.*\ndestinataires.*\nremercions.*\nautorisee.*\nd.*\nLe.*\ncontenues.*\nEdmond.*\nRoth.*\nlo.*\nRoth.*\ninfo.*\nFranc.*\n.2.*", re.I),
    BARBRO_C_EHNBOM: re.compile(r"Barbro C.? Ehn.*\nChairman, Swedish-American.*\n((Office|Cell|Sweden):.*\n)*(360.*\nNew York.*)?"),
    DANIEL_SIAD: re.compile(r"Confidentiality Notice: The information contained in this electronic message is PRIVILEGED and confidential information intended only for the use of the individual entity or entities named as recipient or recipients. If the reader is not the intended recipient, be hereby notified that any dissemination, distribution or copy of this communication is strictly prohibited. If you have received this communication in error, please notify me immediately by electronic mail or by telephone and permanently delete this message from your computer system. Thank you.".replace(' ', r'\s*'), re.IGNORECASE),
    DANNY_FROST: re.compile(r"Danny Frost\nDirector.*\nManhattan District.*\n212.*", re.IGNORECASE),
    DARREN_INDYKE: re.compile(r"DARREN K. INDYKE.*?\**\nThe information contained in this communication.*?Darren K.[\n\s]+?[Il]ndyke(, PLLC)? — All rights reserved\.? ?\n\*{50,120}(\n\**)?", re.DOTALL),
    DAVID_INGRAM: re.compile(r"Thank you in advance.*\nDavid Ingram.*\nCorrespondent\nReuters.*\nThomson.*(\n(Office|Mobile|Reuters.com).*)*"),
    DEEPAK_CHOPRA: re.compile(fr"({DEEPAK_CHOPRA}( MD)?\n)?2013 Costa Del Mar Road\nCarlsbad, CA 92009(\n(Chopra Foundation|Super Genes: Unlock.*))?(\nJiyo)?(\nChopra Center for Wellbeing)?(\nHome: Where Everyone is Welcome)?"),
    EDUARDO_ROBLES: re.compile(fr"(• )?email:.*\n(• )?email:\n(• )?website: www.creativekingdom.com\n(• )?address: 5th Floor Office No:504 Aspect Tower,\nBusiness Bay, Dubai United Arab Emirates."),
    JEFFREY_EPSTEIN: re.compile(r"((\*+|please note)\n+)?(> )?(• )?(» )?The information contained in this communication is\n(> )*(» )?confidential.*?all attachments.( copyright -all rights reserved?)?", re.DOTALL),
    JESSICA_CADWELL: re.compile(r"(f.*\n)?Certified Para.*\nFlorida.*\nBURMAN.*\n515.*\nSuite.*\nWest Palm.*(\nTel:.*)?(\nEmail:.*)?", re.IGNORECASE),
    KEN_JENNE: re.compile(r"Ken Jenne\nRothstein.*\n401 E.*\nFort Lauderdale.*", re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r"Please direct all scheduling.*\nFollow me on twitter.*\nwww.larrysummers.*", re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r"Lawrence (M. )?Krauss\n(Director.*\n)?(Co-director.*\n)?Foundation.*\nSchool.*\n(Co-director.*\n)?(and Director.*\n)?Arizona.*(\nResearch.*\nOri.*\n(krauss.*\n)?origins.*)?", re.IGNORECASE),
    MARTIN_WEINBERG: re.compile(r"(Martin G. Weinberg, Esq.\n20 Park Plaza((, )|\n)Suite 1000\nBoston, MA 02116(\n61.*)?(\n.*([cC]ell|Office))*\n)?This Electronic Message contains.*?contents of this message is.*?prohibited.", re.DOTALL),
    PETER_MANDELSON: re.compile(r'Disclaimer This email and any attachments to it may be.*?with[ \n]+number(.*?EC4V[ \n]+6BJ)?', re.DOTALL | re.IGNORECASE),
    PAUL_BARRETT: re.compile(r"Paul Barrett[\n\s]+Alpha Group Capital LLC[\n\s]+(142 W 57th Street, 11th Floor, New York, NY 10019?[\n\s]+)?(al?[\n\s]*)?ALPHA GROUP[\n\s]+CAPITAL"),
    RICHARD_KAHN: re.compile(fr'Richard Kahn[\n\s]+HBRK Associates Inc.?[\n\s]+((301 East 66th Street, Suite 1OF|575 Lexington Avenue,? 4th Floor,?)[\n\s]+)?New York, (NY|New York) 100(22|65)(\s+(Tel?|Phone)( I|{REDACTED})?\s+Fa[x",]?(_|{REDACTED})*\s+[Ce]el?l?)?', re.IGNORECASE),
    ROSS_GOW: re.compile(r"Ross Gow\nManaging Partner\nACUITY Reputation Limited\n23 Berkeley Square\nLondon.*\nMobile.*\nTel"),
    STEVEN_PFEIFFER: re.compile(r"Steven\nSteven .*\nAssociate.*\nIndependent Filmmaker Project\nMade in NY.*\n30 .*\nBrooklyn.*\n(p:.*\n)?www\.ifp.*", re.IGNORECASE),
    'Susan Edelman': re.compile(r'Susan Edel.*\nReporter\n1211.*\n917.*\nsedelman.*', re.IGNORECASE),
    TERRY_KAFKA: re.compile(r"((>|I) )?Terry B.? Kafka.*\n(> )?Impact Outdoor.*\n(> )?5454.*\n(> )?Dallas.*\n((> )?c?ell.*\n)?(> )?Impactoutdoor.*(\n(> )?cell.*)?", re.IGNORECASE),
    TOM_PRITZKER: re.compile(r"The contents of this email message.*\ncontain confidential.*\n(not )?the intended.*\n(error|please).*\n(you )?(are )?not the.*\n(this )?message.*"),
    TONJA_HADDAD_COLEMAN: re.compile(fr"Tonja Haddad Coleman.*\nTonja Haddad.*\nAdvocate Building\n315 SE 7th.*(\nSuite.*)?\nFort Lauderdale.*(\n({REDACTED} )?facsimile)?(\nwww.tonjahaddad.com?)?(\nPlease add this efiling.*\nThe information.*\nyou are not.*\nyou are not.*)?", re.IGNORECASE),
    UNKNOWN: re.compile(r"(This message is directed to and is for the use of the above-noted addressee only.*\nhereon\.)", re.DOTALL),
}

MAILING_LISTS = [
    CAROLYN_RANGEL,
    INTELLIGENCE_SQUARED,
    'middle.east.update@hotmail.com',
    JP_MORGAN_USGIO,
]

BCC_LISTS = JUNK_EMAILERS + MAILING_LISTS

TRUNCATE_ALL_EMAILS_FROM = BCC_LISTS + [
    'Alan S Halperin',
    BILL_SIEGEL,
    LISA_NEW,
    'Mitchell Bard',
    PAUL_KRASSNER,
    'Skip Rimer',
    'Steven Victor MD',
    TERRY_KAFKA,
]

# These IDs will be appended to INTERESTING_EMAIL_IDS
INTERESTING_TRUNCATION_LENGTHS = {
    '023627': 16_800,  # Micheal Wolff article with brock pierce
    '030245': None,    # Epstein rationalizes his behavior in an open letter to the world
    '030781': None,    # Bannon email about crypto coin issues
    '032906': None,    # David Blaine email
    '026036': 6000,    # Gino Yu blockchain mention
    '029609': None,    # Joi Ito
    '025233': None,    # Reputation.com discussion
    '017827': None,    # Bannon / Peggy Siegal email about netflix doc on Epstein
    '030222': None,    # Ross Gow / Ghislaine correspondence
    '026028': None,    # Larry Summers / Karim Wade intro
    '029545': None,    # Tyler Shears reputation
    '025812': None,    # Tyler Shears reputation
    '029914': 4500,    # Lord Mandelson russian investments
    '033453': None,    # "Just heard you were telling people that you heard I asked Trump for a million dollars"
    '031320': None,    # Epstein Gratitude foundation
    '031036': None,    # Barbro Ehnbom talking about Swedish girl
    '023454': 1878,    # Email invitation sent to tech CEOs + Epstein
    '029342': 2000,    # Hakeem Jeffries
}

TRUNCATION_LENGTHS = {
    **INTERESTING_TRUNCATION_LENGTHS,
    '031791': None,    # First email in Jessica Cadwell chain about service of legal documents
    '023208': None,    # Long discussion about leon black's finances
    '028589': None,    # Long thread with Reid Weingarten
}

# These are long forwarded articles so we force a trim to 1,333 chars if these strings exist
TRUNCATE_TERMS = [
    'The rebuilding of Indonesia',
    'Dominique Strauss-Kahn',
    'THOMAS L. FRIEDMAN',
    'a sleek, briskly paced film whose title suggests a heist movie',
    'quote from The Colbert Report distinguishes',
    'co-inventor of the GTX Smart Shoe',
    'my latest Washington Post column',
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
    # Robert Kuhn
    'The US trade war against China: The view from Beijing',
    # Tom / Paul Krassner
    'I forgot to post my cartoon from week before last, about Howard Schultz',
    # Bannon
    "Bannon the European: He's opening the populist fort in Brussels",
    "Steve Bannon doesn't do subtle.",
    'The Department of Justice lost its latest battle with Congress',
    "Donald Trump's newly named chief strategist and senior counselor",
    # Diane Ziman
    'I was so proud to see him speak at the Women',
    # lawyers
    'recuses itself from Jeffrey Epstein case',
    # Krauss
    'On confronting dogma, I of course agree',
    'I did neck with that woman, but never forced myself on her',
    'It is hard to know how to respond to a list of false',
    'The Women in the World Summit opens April 12',
    'lecture in Heidelberg Oct 14 but they had to cancel',
    # Nikolic
    'people from LifeBall',
    # Epstein
    'David Ben Gurion was asked why he, after 2000',
    # Lisa New
    'The raw materials for that period include interviews',
    'Whether you donated to Poetry in America through',
    # Random
    'Little Hodiaki',
    "It began with deep worries regarding China's growth path",
    'https://www.washingtonpost.com/politics/2018/09/04/transcript-phone-call',
]

METADATA_FIELDS = [
    'is_junk_mail',
    'is_mailing_list',
    'recipients',
    'sent_from_device',
    'subject',
]

# Note the line repair happens *after* 'Importance: High' is removed
LINE_REPAIR_MERGES = {
    '017523': 4,
    '019407': [2, 4],
    '021729': 2,
    '031764': 3,
    '029433': 3,
    '033271': 3,
    '022673': 9,
    '022684': 9,
    '022695': 4,
    '029773': [2, 5],
    '023067': 3,
    '025790': 2,
    '029841': 3,
    '026345': 3,
    '026609': 4,
    '033299': 3,
    '030315': [3, 5],
    '029831': [3, 6],
    '026829': 3,
    '026924': [2, 4],
    '028931': [3, 6],
    '029154': [2, 5],
    '029163': [2, 5],
    '029282': 2,
    '029402': 5,
    '029498': 2,
    '029501': 2,
    '029835': [2, 4],
    '029889': 2,
    '029545': [3, 5],
    '029976': 3,
    '030299': [7, 10],
    '030381': [2, 4],
    '030384': [2, 4],
    '030626': 2,
    '030999': [2, 4],
    '031384': 2,
    '031428': 2,
    '031442': 0,
    '031980': [2, 4],
    '032063': [3, 5],
    '032272': 3,
    '032405': 4,
    '033097': 2,
    '033144': [2, 4],
    '033217': 3,
    '033228': [3, 5],
    '033357': [2, 4],
    '033486': [7, 9],
    '033512': 2,
    '033575': [2, 4],
    '033576': 3,
    '033583': 2,
}


@dataclass
class Email(Communication):
    """
    Attributes:
        actual_text (str) - best effort at the text actually sent in this email, excluding quoted replies and forwards
        config (EmailCfg | None) - manual config for this email (if it exists)
        header (EmailHeader) - header data extracted from the text (from/to/sent/subject etc)
        recipients (list[Name]) - who this email was sent to
        sent_from_device (str | None) - "Sent from my iPhone" style signature (if it exists)
        signature_substitution_counts (dict[str, int]) - count of how many times a signature was replaced with <...snipped...> for each participant
    """
    actual_text: str = field(init=False)
    config: EmailCfg | None = None
    header: EmailHeader = field(init=False)
    recipients: list[Name] = field(default_factory=list)
    sent_from_device: str | None = None
    signature_substitution_counts: dict[str, int] = field(default_factory=dict)  # defaultdict breaks asdict :(
    _line_merge_arguments: list[tuple[int] | tuple[int, int]] = field(default_factory=list)

    # For logging how many headers we prettified while printing, kind of janky
    rewritten_header_ids: ClassVar[set[str]] = set([])

    def __post_init__(self):
        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)

        # Special handling for copying properties out of the config for the document this one was extracted from
        if self.is_local_extract_file():
            self.url_slug = LOCAL_EXTRACT_REGEX.sub('', file_stem_for_id(self.file_id))
            extracted_from_doc_id = self.url_slug.split('_')[-1]

            if extracted_from_doc_id in ALL_FILE_CONFIGS:
                self._set_config_for_extracted_file(ALL_FILE_CONFIGS[extracted_from_doc_id])

        super().__post_init__()

        if self.config and self.config.recipients:
            self.recipients = self.config.recipients
        else:
            for recipient in self.header.recipients():
                self.recipients.extend(self._extract_emailer_names(recipient))

            # Assume mailing list emails are to Epstein
            if self.author in BCC_LISTS and (self.is_note_to_self() or not self.recipients):
                self.recipients = [JEFFREY_EPSTEIN]

        # Remove self CCs but preserve self emails
        if not self.is_note_to_self():
            self.recipients = [r for r in self.recipients if r != self.author]

        self.recipients = sorted(list(set(self.recipients)), key=lambda r: r or UNKNOWN)
        self.text = self._prettify_text()
        self.actual_text = self._actual_text()
        self.sent_from_device = self._sent_from_device()

    def attachments(self) -> list[str]:
        return (self.header.attachments or '').split(';')

    def info_txt(self) -> Text:
        email_type = 'fwded article' if self.is_fwded_article() else 'email'
        txt = Text(f"OCR text of {email_type} from ", style='grey46').append(self.author_txt())

        if self.config and self.config.is_attribution_uncertain:
            txt.append(f" {QUESTION_MARKS}", style=self.author_style())

        txt.append(' to ').append(self.recipients_txt())
        return txt.append(highlighter(f" probably sent at {self.timestamp}"))

    def is_fwded_article(self) -> bool:
        return bool(self.config and self.config.is_fwded_article)

    def is_junk_mail(self) -> bool:
        return self.author in JUNK_EMAILERS

    def is_mailing_list(self) -> bool:
        return self.author in MAILING_LISTS or self.is_junk_mail()

    def is_note_to_self(self) -> bool:
        return self.recipients == [self.author]

    def metadata(self) -> Metadata:
        local_metadata = asdict(self)
        local_metadata['is_junk_mail'] = self.is_junk_mail()
        local_metadata['is_mailing_list'] = self.is_junk_mail()
        local_metadata['subject'] = self.subject() or None
        metadata = super().metadata()
        metadata.update({k: v for k, v in local_metadata.items() if v and k in METADATA_FIELDS})
        return metadata

    def recipients_txt(self, max_full_names: int = 2) -> Text:
        """Text object with comma separated colored versions of all recipients."""
        recipients = [r or UNKNOWN for r in self.recipients] if len(self.recipients) > 0 else [UNKNOWN]

        # Use just the last name for each recipient if there's 3 or more recipients
        return join_texts([
            Text(r if len(recipients) <= max_full_names else extract_last_name(r), style=get_style_for_name(r))
            for r in recipients
        ], join=', ')

    def subject(self) -> str:
        if self.config and self.config.subject:
            return self.config.subject
        else:
            return self.header.subject or ''

    def summary(self) -> Text:
        """One line summary mostly for logging."""
        txt = self._summary()

        if len(self.recipients) > 0:
            txt.append(', ').append(key_value_txt('recipients', self.recipients_txt()))

        return txt.append(CLOSE_PROPERTIES_CHAR)

    def _actual_text(self) -> str:
        """The text that comes before likely quoted replies and forwards etc."""
        if self.config and self.config.actual_text is not None:
            return self.config.actual_text

        text = '\n'.join(self.text.split('\n')[self.header.num_header_rows:]).strip()

        if self.config and self.config.fwded_text_after:
            return text.split(self.config.fwded_text_after)[0].strip()
        elif self.header.num_header_rows == 0:
            return self.text

        self.log_top_lines(20, "Raw text:", logging.DEBUG)
        self.log(f"With header removed:\n{text[0:500]}\n\n", logging.DEBUG)
        reply_text_match = REPLY_TEXT_REGEX.search(text)

        if reply_text_match:
            actual_num_chars = len(reply_text_match.group(1))
            actual_text_pct = f"{(100 * float(actual_num_chars) / len(text)):.1f}%"
            logger.debug(f"'{self.url_slug}': actual_text() reply_text_match is {actual_num_chars:,} chars ({actual_text_pct} of {len(text):,})")
            text = reply_text_match.group(1)

        # If all else fails look for lines like 'From: blah', 'Subject: blah', and split on that.
        for field_name in REPLY_SPLITTERS:
            field_string = f'\n{field_name}'

            if field_string not in text:
                continue

            pre_from_text = text.split(field_string)[0]
            actual_num_chars = len(pre_from_text)
            actual_text_pct = f"{(100 * float(actual_num_chars) / len(text)):.1f}%"
            logger.debug(f"'{self.url_slug}': actual_text() fwd_text_match is {actual_num_chars:,} chars ({actual_text_pct} of {len(text):,})")
            text = pre_from_text
            break

        return text.strip()

    def _border_style(self) -> str:
        """Color emails from epstein to others with the color for the first recipient."""
        if self.author == JEFFREY_EPSTEIN and len(self.recipients) > 0:
            style = get_style_for_name(self.recipients[0])
        else:
            style = self.author_style()

        return style.replace('bold', '').strip()

    def _extract_author(self) -> None:
        self._extract_header()
        super()._extract_author()

        if not self.author and self.header.author:
            authors = self._extract_emailer_names(self.header.author)
            self.author = authors[0] if (len(authors) > 0 and authors[0]) else None

    def _extract_emailer_names(self, emailer_str: str) -> list[str]:
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

    def _extract_header(self) -> None:
        """Extract an EmailHeader object from the OCR text."""
        header_match = EMAIL_SIMPLE_HEADER_REGEX.search(self.text)

        if header_match:
            self.header = EmailHeader.from_header_lines(header_match.group(0))

            if self.header.is_empty():
                self.header.repair_empty_header(self.lines)
        else:
            log_level = logging.INFO if self.config else logging.WARNING
            self.log_top_lines(msg='No email header match found!', level=log_level)
            self.header = EmailHeader(field_names=[])

        logger.debug(f"{self.file_id} extracted header\n\n{self.header}\n")

    def _extract_timestamp(self) -> datetime:
        if self.config and self.config.timestamp:
            return self.config.timestamp
        elif self.header.sent_at:
            timestamp = _parse_timestamp(self.header.sent_at)

            if timestamp:
                return timestamp

        searchable_lines = self.lines[0:MAX_NUM_HEADER_LINES]
        searchable_text = '\n'.join(searchable_lines)
        date_match = DATE_HEADER_REGEX.search(searchable_text)

        if date_match:
            timestamp = _parse_timestamp(date_match.group(1))

            if timestamp:
                return timestamp

        logger.debug(f"Failed to find timestamp, falling back to parsing {MAX_NUM_HEADER_LINES} lines...")

        for line in searchable_lines:
            if not TIMESTAMP_LINE_REGEX.search(line):
                continue

            timestamp = _parse_timestamp(line)

            if timestamp:
                logger.debug(f"Fell back to timestamp {timestamp} in line '{line}'...")
                return timestamp

        raise RuntimeError(f"No timestamp found in '{self.file_path.name}' top lines:\n{searchable_text}")

    def _idx_of_nth_quoted_reply(self, n: int = MAX_QUOTED_REPLIES, text: str | None = None) -> int | None:
        """Get position of the nth 'On June 12th, 1985 [SOMEONE] wrote:' style line in self.text."""
        if text is None:
            header_offset = len(self.header.header_chars)
            text = self.text[header_offset:]
        else:
            header_offset = 0

        for i, match in enumerate(QUOTED_REPLY_LINE_REGEX.finditer(text)):
            if i >= n:
                return match.end() + header_offset - 1

    def _merge_lines(self, idx: int, idx2: int | None = None) -> None:
        """Combine lines numbered 'idx' and 'idx2' into a single line (idx2 defaults to idx + 1)."""
        if idx2 is None:
            self._line_merge_arguments.append((idx,))
            idx2 = idx + 1
        else:
            self._line_merge_arguments.append((idx, idx2))

        lines = self.lines[0:idx]

        if idx2 <= idx:
            raise RuntimeError(f"idx2 ({idx2}) must be greater than idx ({idx})")
        elif idx2 == (idx + 1):
            lines += [self.lines[idx] + ' ' + self.lines[idx + 1]] + self.lines[idx + 2:]
        else:
            lines += [self.lines[idx] + ' ' + self.lines[idx2]] + self.lines[idx + 1:idx2] + self.lines[idx2 + 1:]

        self._set_computed_fields(lines=lines)

    def _prettify_text(self) -> str:
        """Add newlines before quoted replies and snip signatures."""
        # Insert line breaks now unless header is broken, in which case we'll do it later after fixing header
        text = self.text if self.header.was_initially_empty else _add_line_breaks(self.text)
        text = REPLY_REGEX.sub(r'\n\1', text)  # Newlines between quoted replies

        for name, signature_regex in EMAIL_SIGNATURE_REGEXES.items():
            signature_replacement = f'<...snipped {name.lower()} legal signature...>'
            text, num_replaced = signature_regex.subn(signature_replacement, text)
            self.signature_substitution_counts[name] = self.signature_substitution_counts.get(name, 0)
            self.signature_substitution_counts[name] += num_replaced

        return collapse_newlines(text).strip()

    def _remove_line(self, idx: int) -> None:
        """Remove a line from self.lines."""
        num_lines = idx * 2
        self.log_top_lines(num_lines, msg=f'before removal of line {idx}')
        del self.lines[idx]
        self._set_computed_fields(lines=self.lines)
        self.log_top_lines(num_lines, msg=f'after removal of line {idx}')

    def _repair(self) -> None:
        """Repair particularly janky files."""
        if BAD_FIRST_LINE_REGEX.match(self.lines[0]):
            self._set_computed_fields(lines=self.lines[1:])

        self._set_computed_fields(lines=[line for line in self.lines if not BAD_LINE_REGEX.match(line)])
        old_text = self.text

        if self.file_id in LINE_REPAIR_MERGES:
            merge = LINE_REPAIR_MERGES[self.file_id]
            merge_args = merge if isinstance(merge, list) else [merge]
            self._merge_lines(*merge_args)

        # These already had 2nd line merged
        if self.file_id in ['030626']:  # Merge 6th and 7th (now 5th and 6th) rows
            self._merge_lines(4)
        elif self.file_id == '029889':
            self._merge_lines(2, 5)
        elif self.file_id in ['029498', '031428']:
            self._merge_lines(2, 4)

        # Multiline
        if self.file_id == '013415':
            for _i in range(2):
                self._merge_lines(4)
        elif self.file_id == '013405':
            for _i in range(2):
                self._merge_lines(4)
        elif self.file_id == '029458':
            for _i in range(3):
                self._merge_lines(4)
        elif self.file_id in ['025233']:
            for _i in range(2):
                self._merge_lines(4)

            self.lines[4] = f"Attachments: {self.lines[4]}"
            self._set_computed_fields(lines=self.lines)
        elif self.file_id in ['023001']:
            for _i in range(3):
                self._merge_lines(5)
        elif self.file_id in ['019105']:
            for _i in range(4):
                self._merge_lines(5)
        elif self.file_id in ['033568']:
            for _i in range(5):
                self._merge_lines(5)
        elif self.file_id in ['025329']:
            for _i in range(9):
                self._merge_lines(2)
        elif self.file_id in ['025812', '031748']:
            for _i in range(2):
                self._merge_lines(3)
        elif self.file_id == '014860':
            self._merge_lines(3)
            self._merge_lines(4)
            self._merge_lines(4)
        elif self.file_id == '029977':
            self._set_computed_fields(text=self.text.replace('Sent 9/28/2012 2:41:02 PM', 'Sent: 9/28/2012 2:41:02 PM'))

            for _i in range(4):
                self._merge_lines(2)

            self._merge_lines(4)
            self._merge_lines(2, 4)
        elif self.file_id in ['033252']:
            for _i in range(2):
                self._merge_lines(9)
        elif self.file_id in ['032637']:
            for _i in range(3):
                self._merge_lines(9)
        elif self.file_id in ['014397']:
            for _i in range(2):
                self._merge_lines(4)
        elif self.file_id in ['022977']:
            for _i in range(10):
                self._merge_lines(9)

        # Bad line removal
        if self.file_id == '025041':
            self._remove_line(4)
            self._remove_line(4)
        elif self.file_id == '029692':
            self._remove_line(3)

        if old_text != self.text:
            self.log(f"Modified text, old:\n\n" + '\n'.join(old_text.split('\n')[0:12]) + '\n')
            self.log_top_lines(12, 'Result of modifications')

        lines = self.repair_ocr_text(OCR_REPAIRS, self.text).split('\n')
        new_lines = []
        i = 0

        # Fix links (remove spaces, merge multiline links to a single line)
        while i < len(lines):
            line = lines[i]

            if LINK_LINE_REGEX.search(line):
                while i < (len(lines) - 1) \
                        and 'http' not in lines[i + 1] \
                        and (lines[i + 1].endswith('/') or any(s in lines[i + 1] for s in URL_SIGNIFIERS) or LINK_LINE2_REGEX.match(lines[i + 1])):
                    logger.debug(f"{self.filename}: Joining link lines\n   1. {line}\n   2. {lines[i + 1]}\n")
                    line += lines[i + 1]
                    i += 1
                    #import pdb;pdb.set_trace()

                line = line.replace(' ', '')
            elif ' http' in line and line.endswith('html'):
                pre_link, post_link = line.split(' http', 1)
                line = f"{pre_link} http{post_link.replace(' ', '')}"

            new_lines.append(line)

            # TODO: hacky workaround to get a working link for HOUSE_OVERSIGHT_032564
            if self.file_id == '032564' and line == 'http://m.huffpost.com/us/entry/us_599f532ae4b0dOef9f1c129d':
                new_lines.append('(ed. note: an archived version of the above link is here: https://archive.is/hJxT3 )')

            i += 1

        self._set_computed_fields(lines=new_lines)

    def _sent_from_device(self) -> str | None:
        """Find any 'Sent from my iPhone' style signature line if it exist in the 'actual_text'."""
        sent_from_match = SENT_FROM_REGEX.search(self.actual_text)

        if sent_from_match:
            sent_from = sent_from_match.group(0)
            return 'S' + sent_from[1:] if sent_from.startswith('sent') else sent_from

    def _set_config_for_extracted_file(self, extracted_from_doc_cfg: DocCfg) -> None:
        """Copy info from original config for file this document was extracted from."""
        if self.file_id in ALL_FILE_CONFIGS:
            self.config = cast(EmailCfg, deepcopy(ALL_FILE_CONFIGS[self.file_id]))
            self.warn(f"Merging existing cfg for '{self.file_id}' with cfg for extracted document...")
        else:
            self.config = EmailCfg(id=self.file_id)

        extracted_from_description = extracted_from_doc_cfg.complete_description()

        if extracted_from_description:
            extracted_description = f"{APPEARS_IN} {extracted_from_description}"

            if isinstance(extracted_from_doc_cfg, EmailCfg):
                extracted_description += ' email'

            if self.config.description:
                self.warn(f"Overwriting description '{self.config.description}' with extract's '{self.config.description}'")

            self.config.description = extracted_description

        self.config.is_interesting = self.config.is_interesting or extracted_from_doc_cfg.is_interesting
        self.log(f"Constructed synthetic config: {self.config}")

    def _truncate_to_length(self) -> int:
        """When printing truncate this email to this length."""
        quote_cutoff = self._idx_of_nth_quoted_reply(text=self.text)  # Trim if there's many quoted replies
        includes_truncate_term = next((term for term in TRUNCATE_TERMS if term in self.text), None)

        if args.whole_file:
            num_chars = len(self.text)
        elif args.truncate:
            num_chars = args.truncate
        elif self.file_id in TRUNCATION_LENGTHS:
            num_chars = TRUNCATION_LENGTHS[self.file_id] or self.file_size()
        elif self.author in TRUNCATE_ALL_EMAILS_FROM or includes_truncate_term:
            num_chars = min(quote_cutoff or MAX_CHARS_TO_PRINT, int(MAX_CHARS_TO_PRINT / 3))
        elif quote_cutoff and quote_cutoff < MAX_CHARS_TO_PRINT:
            num_chars = quote_cutoff
        else:
            num_chars = MAX_CHARS_TO_PRINT

        if num_chars != MAX_CHARS_TO_PRINT and not self.is_duplicate():
            log_args = {
                'num_chars': num_chars,
                'author_truncate': self.author in TRUNCATE_ALL_EMAILS_FROM,
                'is_fwded_article': self.is_fwded_article(),
                'is_quote_cutoff': quote_cutoff == num_chars,
                'includes_truncate_term': json.dumps(includes_truncate_term) if includes_truncate_term else None,
                'quote_cutoff': quote_cutoff,
            }

            logger.debug(f'{self.summary()} truncating: ' + ', '.join([f"{k}={v}" for k, v in log_args.items() if v]) + '\n')

        return num_chars

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        logger.debug(f"Printing '{self.filename}'...")
        should_rewrite_header = self.header.was_initially_empty and self.header.num_header_rows > 0
        num_chars = self._truncate_to_length()
        trim_footer_txt = None
        text = self.text

        # Truncate long emails but leave a note explaining what happened w/link to source document
        if len(text) > num_chars:
            text = text[0:num_chars]
            doc_link_markup = epstein_media_doc_link_markup(self.url_slug, self.author_style())
            trim_note = f"<...trimmed to {num_chars} characters of {self.length()}, read the rest at {doc_link_markup}...>"
            trim_footer_txt = Text.from_markup(wrap_in_markup_style(trim_note, 'dim'))

        # Rewrite broken headers where the values are on separate lines from the field names
        if should_rewrite_header:
            configured_actual_text = self.config.actual_text if self.config and self.config.actual_text else None
            num_lines_to_skip = self.header.num_header_rows
            lines = []

            # Emails w/configured 'actual_text' are particularly broken; need to shuffle some lines
            if configured_actual_text is not None:
                num_lines_to_skip += 1
                lines += [cast(str, configured_actual_text), '\n']

            lines += text.split('\n')[num_lines_to_skip:]
            text = self.header.rewrite_header() + '\n' + '\n'.join(lines)
            text = _add_line_breaks(text)  # This was skipped when _prettify_text() w/a broken header so we do it now
            self.rewritten_header_ids.add(self.file_id)

        lines = [
            Text.from_markup(f"[link={line}]{line}[/link]") if line.startswith('http') else Text(line)
            for line in text.split('\n')
        ]

        text = join_texts(lines, '\n')

        email_txt_panel = Panel(
            highlighter(text).append('\n\n').append(trim_footer_txt) if trim_footer_txt else highlighter(text),
            border_style=self._border_style(),
            expand=False,
            subtitle=REWRITTEN_HEADER_MSG if should_rewrite_header else None,
        )

        yield self.file_info_panel()
        yield Padding(email_txt_panel, (0, 0, 1, INFO_INDENT))

        if should_rewrite_header:
            self.log_top_lines(self.header.num_header_rows + 4, f'Original header:')

    @staticmethod
    def build_emails_table(emails: list['Email'], name: Name = '', title: str = '', show_length: bool = False) -> Table:
        """Turn a set of Emails into a Table."""
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
        )

        for email in emails:
            fields = [
                email.epstein_media_link(link_txt=email.timestamp_without_seconds(), style=link_style),
                email.author_txt(),
                email.recipients_txt(max_full_names=1),
                f"{email.length()}",
                email.subject(),
            ]

            if not show_length:
                del fields[3]

            table.add_row(*fields)

        return table


def _add_line_breaks(email_text: str) -> str:
    return EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX.sub(r'\n\1\n', email_text).strip()


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
