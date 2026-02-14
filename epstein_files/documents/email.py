import json
import logging
import re
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
from epstein_files.documents.emails.email_header import (EMAIL_SIMPLE_HEADER_REGEX,
     EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX, FIELD_NAMES, FIELDS_COLON_PATTERN, EmailHeader)
from epstein_files.documents.emails.emailers import extract_emailer_names
from epstein_files.documents.other_file import OtherFile
from epstein_files.util.constant.names import *
from epstein_files.util.constant.strings import REDACTED
from epstein_files.util.constants import *
from epstein_files.util.data import AMERICAN_TIME_REGEX, TIMEZONE_INFO, collapse_newlines, remove_timezone, uniquify
from epstein_files.util.doc_cfg import EmailCfg, Metadata
from epstein_files.util.file_helper import extract_file_id, file_stem_for_id
from epstein_files.util.highlighted_group import JUNK_EMAILERS, get_style_for_name
from epstein_files.util.logging import logger
from epstein_files.util.rich import *

BAD_FIRST_LINE_REGEX = re.compile(r'^(>>|Grant_Smith066474"eMailContent.htm|LOVE & KISSES)$')
BAD_LINE_REGEX = re.compile(r'^(>;?|\d{1,2}|PAGE INTENTIONALLY LEFT BLANK|Classification: External Communication|Hide caption|Importance:?\s*High|[iI,•]|[1i] (_ )?[il]|, [-,]|L\._|_filtered|.*(yiv0232|font-family:|margin-bottom:).*)$')
BAD_SUBJECT_CONTINUATIONS = ['orwarded', 'Hi ', 'Sent ', 'AmLaw', 'Original Message', 'Privileged', 'Sorry', '---']
FIELDS_COLON_REGEX = re.compile(FIELDS_COLON_PATTERN)
LINK_LINE_REGEX = re.compile(f"^[>• ]*htt")
LINK_LINE2_REGEX = re.compile(r"^[-\w.%&=/]{5,}$")
QUOTED_REPLY_LINE_REGEX = re.compile(r'(\nFrom:(.*)|wrote:)\n', re.IGNORECASE)
REPLY_TEXT_REGEX = re.compile(rf"^(.*?){REPLY_LINE_PATTERN}", re.DOTALL | re.IGNORECASE | re.MULTILINE)

BAD_TIMEZONE_REGEX = re.compile(fr'\((UTC|GMT\+\d\d:\d\d)\)|{REDACTED}')
DATE_HEADER_REGEX = re.compile(r'(?:Date|Sent):? +(?!by|from|to|via)([^\n]{6,})\n')
TIMESTAMP_LINE_REGEX = re.compile(r"\d+:\d+")
LOCAL_EXTRACT_REGEX = re.compile(r"_\d$")

REWRITTEN_HEADER_MSG = "(janky OCR header fields were prettified, check source if something seems off)"
URL_SIGNIFIERS = ['?amp', 'amp?', 'cd=', 'click', 'CMP=', 'contentId', 'ft=', 'gclid', 'htm', 'mp=', 'keywords=', 'Id=', 'module=', 'mpweb', 'nlid=', 'ref=', 'smid=', 'sp=', 'usg=', 'utm']
APPEARS_IN = 'appears in'

MAX_NUM_HEADER_LINES = 14
MAX_QUOTED_REPLIES = 1
NUM_WORDS_IN_LAST_QUOTE = 6

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
    # Headers
    re.compile(r"^From "): 'From: ',
    re.compile(r"^(Sent|Subject) (?![Ff]rom|[Vv]ia)", re.MULTILINE): r'\1: ',
    'I nline-Images:': 'Inline-Images:',
    # Names / email addresses
    'Alireza lttihadieh': ALIREZA_ITTIHADIEH,
    'Miroslav Laj6ak': MIROSLAV_LAJCAK,
    'Ross G°w': ROSS_GOW,
    'Torn Pritzker': TOM_PRITZKER,
    re.compile(r' Banno(r]?|\b)'): ' Bannon',
    re.compile(r'gmax ?[1l] ?[@g]ellmax.c ?om'): 'gmax1@ellmax.com',
    re.compile(r"[ijlp']ee[vy]acation[©@a(&,P ]{1,3}g?mail.com"): 'jeevacation@gmail.com',
    'gyahoo.com': '@yahoo.com',
    # Signatures
    'BlackBerry by AT &T': 'BlackBerry by AT&T',
    'BlackBerry from T- Mobile': 'BlackBerry from T-Mobile',
    'Envoy& de': 'Envoyé de',
    'from Samsung Mob.le': 'from Samsung Mobile',
    'gJeremyRubin': '@JeremyRubin',
    'Sent from Mabfl': 'Sent from Mobile',  # NADIA_MARCINKO signature bad OCR
    'twitter glhsummers': 'twitter @lhsummers',
    re.compile(r"from my ['!]Phone"): 'from my iPhone',
    re.compile(r"[cC]o-authored with i ?Phone auto-correct"): "Co-authored with iPhone auto-correct",
    re.compile(r"twitter\.com[i/][lI]krauss[1lt]"): "twitter.com/lkrauss1",
    re.compile(r'from my BlackBerry[0°] wireless device'): 'from my BlackBerry® wireless device',
    re.compile(r'^INW$', re.MULTILINE): REDACTED,
    # links
    'Imps ://': 'https://',
    'classified-intelligence-\nmichael-flynn-trump': 'classified-intelligence-michael-flynn-trump',
    'on-accusers-rose-\nmcgowan/ ': 'on-accusers-rose-\nmcgowan/\n',
    'the-truth-\nabout-the-bitcoin-foundation/ )': 'the-truth-about-the-bitcoin-foundation/ )\n',
    'woody-allen-jeffrey-epsteins-\nsociety-friends-close-ranks/ ---': 'woody-allen-jeffrey-epsteins-society-friends-close_ranks/\n',
    ' https://www.theguardian.com/world/2017/may/29/close-friend-trump-thomas-barrack-\nalleged-tax-evasion-italy-sardinia?CMP=share btn fb': '\nhttps://www.theguardian.com/world/2017/may/29/close-friend-trump-thomas-barrack-alleged-tax-evasion-italy-sardinia?CMP=share_btn_fb',
    re.compile(r'timestopics/people/t/landon jr thomas/inde\n?x\n?\.\n?h\n?tml'): 'timestopics/people/t/landon_jr_thomas/index.html',
    re.compile(r" http ?://www. ?dailymail. ?co ?.uk/news/article-\d+/Troub ?led-woman-history-drug-\n?us ?e-\n?.*html"): '\nhttp://www.dailymail.co.uk/news/article-3914012/Troubled-woman-history-drug-use-claimed-assaulted-Donald-Trump-Jeffrey-Epstein-sex-party-age-13-FABRICATED-story.html',
    re.compile(r"http.*steve-bannon-trump-tower-\n?interview-\n?trumps-\n?strategist-plots-\n?new-political-movement-948747"): "\nhttp://www.hollywoodreporter.com/news/steve-bannon-trump-tower-interview-trumps-strategist-plots-new-political-movement-948747",
    # Subject lines
    "Arrested in\nInauguration Day Riot": "Arrested in Inauguration Day Riot",
    "as Putin Mayhem Tests President's Grip\non GOP": "as Putin Mayhem Tests President's Grip on GOP",
    "avoids testimony from alleged\nvictims": "avoids testimony from alleged victims",
    "It's a first, but the buyer's\nanonymous": "It's a first, but the buyer's anonymous",
    "but\nwatchdogs say probe is tainted": "watchdogs say probe is tainted",
    "Christmas comes\nearly for most of macro": "Christmas comes early for most of macro",            # 023717
    "but majority still made good\nmoney because": "but majority still made good money because",      # 023717
    "COVER UP SEX ABUSE CRIMES\nBY THE WHITE HOUSE": "COVER UP SEX ABUSE CRIMES BY THE WHITE HOUSE",
    'Priebus, used\nprivate email accounts for': 'Priebus, used private email accounts for',
    "War on the Investigations\nEncircling Him": "War on the Investigations Encircling Him",
    "Subject; RE": "Subject: RE",
    "straining relations between UK and\nAmerica": "straining relations between UK and America",
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
    'Saw Matt C with DTF at golf': 'Saw Matt C with DJT at golf',
    re.compile(r"[i. ]*Privileged[- ]*Redacted[i. ]*"): '<PRIVILEGED - REDACTED>',
}

EMAIL_SIGNATURE_REGEXES = {
    ARIANE_DE_ROTHSCHILD: re.compile(r"Ensemble.*\nCe.*\ndestinataires.*\nremercions.*\nautorisee.*\nd.*\nLe.*\ncontenues.*\nEdmond.*\nRoth.*\nlo.*\nRoth.*\ninfo.*\nFranc.*\n.2.*", re.I),
    BARBRO_C_EHNBOM: re.compile(r"Barbro C.? Ehn.*\nChairman, Swedish-American.*\n((Office|Cell|Sweden):.*\n)*(360.*\nNew York.*)?"),
    BRAD_KARP: re.compile(r"This message is intended only for the use of the Addressee and may contain information.*\nnot the intended recipient, you are hereby notified.*\nreceived this communication in error.*"),
    BROCK_PIERCE: re.compile(r"IMPORTANT NOTICE: This.*\n(individual.*\nthat is.*\nlaw.*\nemployee.*\nrecipient.*|may contain info.*\nreader of this.*)|(Mobile?:?.*\n)?(Skype:.*\n)?E:.*\n(W:.*\n)?(Follow me.*\n)?Co-invest.*(\nLinked.*)?"),
    DANIEL_SIAD: re.compile(r"Confidentiality Notice: The information contained in this electronic message is PRIVILEGED and confidential information intended only for the use of the individual entity or entities named as recipient or recipients. If the reader is not the intended recipient, be hereby notified that any dissemination, distribution or copy of this communication is strictly prohibited. If you have received this communication in error, please notify me immediately by electronic mail or by telephone and permanently delete this message from your computer system. Thank you.".replace(' ', r'\s*'), re.IGNORECASE),
    DANNY_FROST: re.compile(r"Danny Frost\nDirector.*\nManhattan District.*\n212.*", re.IGNORECASE),
    DARREN_INDYKE: re.compile(r"DARREN K. INDYKE.*?\**\nThe information contained in this communication.*?Darren K.[\n\s]+?[Il]ndyke(, PLLC)? — All rights reserved\.? ?\n\*{50,120}(\n\**)?", re.DOTALL),
    DAVID_FISZEL: re.compile(r"This e-mail and any file.*\nmail and/or any file.*\nmail or any.*\nreceived.*\nmisdirected.*"),
    DAVID_INGRAM: re.compile(r"Thank you in advance.*\nDavid Ingram.*\nCorrespondent\nReuters.*\nThomson.*(\n(Office|Mobile|Reuters.com).*)*"),
    DEEPAK_CHOPRA: re.compile(fr"({DEEPAK_CHOPRA}( MD)?\n)?2013 Costa Del Mar Road\nCarlsbad, CA 92009(\n(Chopra Foundation|Super Genes: Unlock.*))?(\nJiyo)?(\nChopra Center for Wellbeing)?(\nHome: Where Everyone is Welcome)?"),
    EDUARDO_ROBLES: re.compile(r"(• )?email:.*\n(• )?email:\n(• )?website: www.creativekingdom.com\n(• )?address: 5th Floor Office No:504 Aspect Tower,\nBusiness Bay, Dubai United Arab Emirates."),
    ERIC_ROTH: re.compile(r"2221 Smithtown Avenue\nLong Island.*\nRonkonkoma.*\n(.1. )?Phone\nFax\nCell\ne-mail"),
    GHISLAINE_MAXWELL: re.compile(r"FACEBOOK\nTWITTER\nG\+\nPINTEREST\nINSTAGRAM\nPLEDGE\nTHE DAILY CATCH"),
    JEANNE_M_CHRISTENSEN: re.compile(r"A?Please consider the environment.*\nThis communication may.*\nWork Product.*\nresponsible.*\nanyone.*\nhereof.*|This communication may contain Confidential.*\nyou are not the addressee.*\nto such person.*\nor delete this.*"),
    JEFFREY_EPSTEIN: re.compile(r"((\*+|please note)\n+)?([>»•]+ )*The information contained i[n=] this communication is\s*([>»] )*confidential.*?all\s+([>»] )*attachments.( copyright [-=]all rights reserved?)?", re.DOTALL),
    JESSICA_CADWELL: re.compile(r"(f.*\n)?Certified Para.*\nFlorida.*\nBURMAN.*\n515.*\nSuite.*\nWest Palm.*(\nTel:.*)?(\nEmail:.*)?", re.IGNORECASE),
    KEN_JENNE: re.compile(r"Ken Jenne\nRothstein.*\n401 E.*\nFort Lauderdale.*", re.IGNORECASE),
    LARRY_SUMMERS: re.compile(r"Please direct all scheduling.*\nFollow me on twitter.*\nwww.larrysummers.*", re.IGNORECASE),
    LAWRENCE_KRAUSS: re.compile(r"Lawrence (M. )?Krauss\n(Director.*\n)?(Co-director.*\n)?Foundation.*\nSchool.*\n(Co-director.*\n)?(and Director.*\n)?Arizona.*(\nResearch.*\nOri.*\n(krauss.*\n)?origins.*)?", re.IGNORECASE),
    LEON_BLACK: re.compile(r"This email and any files transmitted with it are confidential and intended solely.*\n(they|whom).*\ndissemination.*\nother.*\nand delete.*"),
    LISA_NEW: re.compile(r"Elisa New\nPowell M. Cabot.*\n(Director.*\n)?Harvard.*\n148.*\n([1I] )?12.*\nCambridge.*\n([1I] )?02138"),
    MARTIN_WEINBERG: re.compile(r"(Martin G. Weinberg, Esq.\n20 Park Plaza((, )|\n)Suite 1000\nBoston, MA 02116(\n61.*?)?(\n.*?([cC]ell|Office))*\n)?This Electronic Message contains.*?contents of this message is.*?prohibited.", re.DOTALL),
    MICHAEL_MILLER: re.compile(r"Michael C. Miller\nPartner\nwww.steptoe.com/mmiller\nSteptoe\n(Privileged.*\n)?(\+1\s+)?direct.*\n(\+1\s+)?(\+1\s+)?fax.*\n(\+1.*)?cell.*\n(www.steptoe.com\n)?This message and any.*\nyou are not.*\nnotify the sender.*"),
    NICHOLAS_RIBIS: re.compile(r"60 Morris Turnpike 2FL\nSummit,? NJ.*\n0:\nF:\n\*{20,}\nCONFIDENTIALITY NOTICE.*\nattachments.*\ncopying.*\nIf you have.*\nthe copy.*\nThank.*\n\*{20,}"),
    PETER_MANDELSON: re.compile(r'Disclaimer This email and any attachments to it may be.*?with[ \n]+number(.*?EC4V[ \n]+6BJ)?', re.DOTALL | re.IGNORECASE),
    PAUL_BARRETT: re.compile(r"Paul Barrett[\n\s]+Alpha Group Capital LLC[\n\s]+(142 W 57th Street, 11th Floor, New York, NY 10019?[\n\s]+)?(al?[\n\s]*)?ALPHA GROUP[\n\s]+CAPITAL"),
    PETER_ATTIA: re.compile(r"The information contained in this transmission may contain.*\n(laws|patient).*\n(distribution|named).*\n(distribution.*\nplease.*|copies.*)"),
    RICHARD_KAHN: re.compile(fr'Richard Kahn[\n\s]+HBRK Associates Inc.?[\n\s]+((301 East 66th Street, Suite 1OF|575 Lexington Avenue,? 4th Floor,?)[\n\s]+)?New York, (NY|New York) 100(22|65)(\s+(Tel?|Phone)( I|{REDACTED})?\s+Fa[x",]?(_|{REDACTED})*\s+[Ce]el?l?)?', re.IGNORECASE),
    ROSS_GOW: re.compile(r"Ross Gow\nManaging Partner\nACUITY Reputation Limited\n23 Berkeley Square\nLondon.*\nMobile.*\nTel"),
    STEPHEN_HANSON: re.compile(r"(> )?Confidentiality Notice: This e-mail transmission.*\n(which it is addressed )?and may contain.*\n(applicable law. If you are not the intended )?recipient you are hereby.*\n(information contained in or attached to this transmission is )?STRICTLY PROHIBITED.*"),
    STEVEN_PFEIFFER: re.compile(r"Steven\nSteven .*\nAssociate.*\nIndependent Filmmaker Project\nMade in NY.*\n30 .*\nBrooklyn.*\n(p:.*\n)?www\.ifp.*", re.IGNORECASE),
    'Susan Edelman': re.compile(r'Susan Edel.*\nReporter\n1211.*\n917.*\nsedelman.*', re.IGNORECASE),
    TERRY_KAFKA: re.compile(r"((>|I) )?Terry B.? Kafka.*\n(> )?Impact Outdoor.*\n(> )?5454.*\n(> )?Dallas.*\n((> )?c?ell.*\n)?(> )?Impactoutdoor.*(\n(> )?cell.*)?", re.IGNORECASE),
    TOM_PRITZKER: re.compile(r"The contents of this email message.*\ncontain confidential.*\n(not )?the intended.*\n(error|please).*\n(you )?(are )?not the.*\n(this )?message.*"),
    TONJA_HADDAD_COLEMAN: re.compile(fr"Tonja Haddad Coleman.*\nTonja Haddad.*\nAdvocate Building\n315 SE 7th.*(\nSuite.*)?\nFort Lauderdale.*(\n({REDACTED} )?facsimile)?(\nwww.tonjahaddad.com?)?(\nPlease add this efiling.*\nThe information.*\nyou are not.*\nyou are not.*)?", re.IGNORECASE),
    UNKNOWN: re.compile(r"(This message is directed to and is for the use of the above-noted addressee only.*\nhereon\.)", re.DOTALL),
    'W Bradford Stephens': re.compile(r"This email \(including.*\n(please.*\n)?it.*\nand do not.*\n(does.*\n)?constitute.*\ninvestment.*\n(info.*\n)?contained.*\nthe.*\s*(sender.*\n)?update.*\nthis.*(\nemail.*)?"),
}

MAILING_LISTS = [
    CAROLYN_RANGEL,
    INTELLIGENCE_SQUARED,
    'middle.east.update@hotmail.com',
    JP_MORGAN_USGIO,
]

BCC_LISTS = JUNK_EMAILERS + MAILING_LISTS

TRUNCATE_EMAILS_FROM_OR_TO = [
    AMANDA_ENS,
    ANTHONY_BARRETT,
    DANIEL_SABBA,
    DIANE_ZIMAN,
    JOSCHA_BACH,
    KATHERINE_KEATING,
    LAWRANCE_VISOSKI,
    LAWRENCE_KRAUSS,
    LISA_NEW,
    MOSHE_HOFFMAN,
    NILI_PRIELL_BARAK,
    PAUL_KRASSNER,
    PAUL_PROSPERI,
    'Susan Edelman',
    TERRY_KAFKA,
]

TRUNCATE_EMAILS_FROM = BCC_LISTS + TRUNCATE_EMAILS_FROM_OR_TO + [
    'Alan S Halperin',
    'Alain Forget',
    ARIANE_DE_ROTHSCHILD,
    AZIZA_ALAHMADI,
    BILL_SIEGEL,
    DAVID_HAIG,
    EDWARD_ROD_LARSEN,
    JOHNNY_EL_HACHEM,
    'Mark Green',
    MELANIE_WALKER,
    'Mitchell Bard',
    PEGGY_SIEGAL,
    ROBERT_LAWRENCE_KUHN,
    ROBERT_TRIVERS,
    'Skip Rimer',
    'Steven Elkman',
    STEVEN_PFEIFFER,
    'Steven Victor MD',
    TERRY_KAFKA,
]

# These are long forwarded articles so we force a trim to 1,333 chars if these strings exist
TRUNCATE_TERMS = [
    'The rebuilding of Indonesia',  # Vikcy ward article
    'a sleek, briskly paced film whose title suggests a heist movie',  # Inside Job
    'Calendar of Major Events, Openings, and Fundraisers',
    'sent over from Marshall Heyman at the WSJ',
    "In recent months, China's BAT collapse",
    'President Obama introduces Jim Yong Kim as his nominee',
    'Trump appears with mobster-affiliated felon at New',
    'Congratulations to the 2019 Hillman Prize recipients',
    "Special counsel Robert Mueller's investigation may face a serious legal obstacle",
    "nearly leak-proof since its inception more than a year ago",
    # Nikolic
    'Nuclear Operator Raises Alarm on Crisis',
    'as responsible for the democratisation of computing and',
    'AROUND 1,000 operational satellites are circling the Earth',
    # Sultan Sulayem
    'co-inventor of the GTX Smart Shoe',
    'my latest Washington Post column',
    # Bannon
    'As Steve Bannon continues his tour of Europe',
    "Bannon the European: He's opening the populist fort in Brussels",
    "Steve Bannon doesn't do subtle.",
    'The Department of Justice lost its latest battle with Congress',
    'pedophile Jeffrey Epstein bought his way out',
    # lawyers
    'recuses itself from Jeffrey Epstein case',
    # Misc
    'people from LifeBall',  # Nikolic
    "It began with deep worries regarding China's growth path",  # Paul Morris
    'A friendly discussion about Syria with a former US State Department',  # Fabrice Aidan
    'The US trade war against China: The view from Beijing',  # Robert Kuhn / Groff
    'This much we know - the Fall elections are shaping up',  # Juleanna Glover / Bannon
]

METADATA_FIELDS = [
    'is_junk_mail',
    'is_mailing_list',
    'recipients',
    'sent_from_device',
    'subject',
]

# Arguments to _merge_lines(). Note the line repair happens *after* 'Importance: High' is removed
LINE_REPAIR_MERGES = {
    '013405': [[4]] * 2,
    '013415': [[4]] * 2,
    '014397': [[4]] * 2,
    '014860': [[3], [4], [4]],
    '017523': [[4]],
    '030367': [[1, 4], [2, 4]],
    '019105': [[5]] * 4,
    '019407': [[2, 4]],
    '022187': [[1, 8], [2, 8], [3, 8], [4, 8]],
    '021729': [[2]],
    '032896': [[2]],
    '033050': [[0, 6], [1, 6], [2, 6], [3, 6], [4, 6]],
    '022949': [[0, 4], [1, 4]],
    '022197': [[0, 5], [1, 5], [3, 5]],
    '021814': [[1, 6], [2, 6], [3, 6], [4, 6]],
    '022190': [[1, 7], [0, 6], [3, 6], [4, 6]],
    '029582': [[0, 5], [1, 5], [3, 5], [3, 5]],
    '022673': [[9]],
    '022684': [[9]],
    '026625': [[0, 7], [1, 7], [2, 7], [3, 7], [4, 7], [5, 7]],
    '026659': [[0, 5], [1, 5]],
    '026764': [[0, 6], [1, 6]],
    '022695': [[4]],
    '022977': [[9]] * 10,
    '023001': [[5]] * 3,
    '023067': [[3]],
    '025233': [[4]] * 2,
    '025329': [[2]] * 9,
    '025790': [[2]],
    '025812': [[3]] * 2,
    '025589': [[3]] * 12,
    '026345': [[3]],
    '026609': [[4]],
    '028921': [[5, 4], [4, 5]],
    '026620': ([[20]] * 4) + [[3, 2]] + ([[2]] * 15) + [[2, 4]],
    '026829': [[3]],
    '026924': [[2, 4]],
    '028728': [[3]],
    '026451': [[3, 5]] * 2,
    '028931': [[3, 6]],
    '029154': [[2, 5]],
    '029163': [[2, 5]],
    '029282': [[2]],
    '029402': [[5]],
    '029433': [[3]],
    '029458': [[4]] * 3,
    '029498': [[2], [2, 4]],
    '029501': [[2]],
    '029545': [[3, 5]],
    '029773': [[2, 5]],
    '029831': [[3, 6]],
    '029835': [[2, 4]],
    '029841': [[3]],
    '029889': [[2], [2, 5]],
    '029976': [[3]],
    '029977': ([[2]] * 4) + [[4], [2, 4]],
    '030299': [[7, 10]],
    '030315': [[3, 5]],
    '030318': [[3, 5]],
    '030381': [[2, 4]],
    '030384': [[2, 4]],
    '030626': [[2], [4]],
    '030861': [[3, 8]],
    '030999': [[2, 4]],
    '031384': [[2]],
    '031428': [[2], [2, 4]],
    '031442': [[0]],
    '031489': [[2, 4], [3, 4], [3, 4], [10]],
    '031619': [[7], [17], [17]],
    '031748': [[3]] * 2,
    '031764': [[3], [8]],  # 8 is just for style fix internally, not header
    '031980': [[2, 4]],
    '032063': [[3, 5]],
    '032272': [[2, 10], [3]],
    '032405': [[4]],
    '032637': [[9]] * 3,
    '033097': [[2]],
    '033144': [[2, 4]],
    '033217': [[3]],
    '033228': [[3, 5]],
    '033252': [[9]] * 2,
    '033271': [[3]],
    '033299': [[3]],
    '033357': [[2, 4]],
    '033486': [[7, 9]],
    '033512': [[2]],
    '026024': [[1, 3], [2, 3]],
    '024923': [[0, 5], [2]],
    '033568': [[5]] * 5,
    '033575': [[2, 4]],
    '033576': [[3]],
    '033583': [[2]],

    # Note DOJ file line adjustments happen *after* DojFile._repair() is called
    'EFTA00039689': [[4]],
}


@dataclass
class Email(Communication):
    """
    Attributes:
        actual_text (str) - Best effort at the text actually sent in this email, excluding quoted replies and forwards.
        config (EmailCfg, optional) - Manual config for this email (if it exists).
        header (EmailHeader) - Header data extracted from the text (from/to/sent/subject etc).
        recipients (list[Name]) - People to whom this email was sent.
        sent_from_device (str, optional) - "Sent from my iPhone" style signature (if it exists).
        signature_substitution_counts (dict[str, int]) - Number of times a signature was replaced with
            <...snipped...> for each participant
    """
    attached_docs: list[OtherFile] = field(default_factory=list)
    actual_text: str = field(init=False)
    config: EmailCfg | None = None
    header: EmailHeader = field(init=False)
    recipients: list[Name] = field(default_factory=list)
    sent_from_device: str | None = None
    signature_substitution_counts: dict[str, int] = field(default_factory=dict)  # defaultdict breaks asdict :(
    _is_first_for_user: bool = False  # Only set when printing
    _line_merge_arguments: list[tuple[int] | tuple[int, int]] = field(default_factory=list)

    # For logging how many headers we prettified while printing, kind of janky
    rewritten_header_ids: ClassVar[set[str]] = set([])

    @property
    def attachments(self) -> list[str]:
        """Returns the string in the header."""
        return (self.header.attachments or '').split(';')

    @property
    def border_style(self) -> str:
        """Color emails from epstein to others with the color for the first recipient."""
        if self.author == JEFFREY_EPSTEIN and len(self.recipients) > 0:
            style = get_style_for_name(self.recipients[0])
        else:
            style = self.author_style

        return style.replace('bold', '').strip()

    @property
    def external_link_markup(self) -> str:
        return epstein_media_doc_link_markup(self.url_slug, self.author_style)

    @property
    def info_txt(self) -> Text:
        email_type = 'fwded article' if self.is_fwded_article else 'email'
        txt = Text(f"OCR text of {email_type} from ", style='grey46').append(self.author_txt)

        if self.config and self.config.is_attribution_uncertain:
            txt.append(f" {QUESTION_MARKS}", style=self.author_style)

        txt.append(' to ').append(self.recipients_txt())
        return txt.append(highlighter(f" probably sent at {self.timestamp}"))

    @property
    def is_fwded_article(self) -> bool:
        if self.config is None:
            return False
        elif self.config.fwded_text_after:
            return self.config.is_fwded_article is not False
        else:
            return bool(self.config.is_fwded_article)

    @property
    def is_junk_mail(self) -> bool:
        return self.author in JUNK_EMAILERS

    @property
    def is_mailing_list(self) -> bool:
        return self.author in MAILING_LISTS or self.is_junk_mail

    @property
    def is_note_to_self(self) -> bool:
        return self.recipients == [self.author]

    @property
    def is_word_count_worthy(self) -> bool:
        if self.is_fwded_article:
            return bool(self.config.fwded_text_after) or len(self.actual_text) < 150
        else:
            return not self.is_mailing_list

    @property
    def metadata(self) -> Metadata:
        local_metadata = asdict(self)
        local_metadata['is_junk_mail'] = self.is_junk_mail
        local_metadata['is_mailing_list'] = self.is_junk_mail
        local_metadata['subject'] = self.subject or None
        metadata = super().metadata
        metadata.update({k: v for k, v in local_metadata.items() if v and k in METADATA_FIELDS})
        return metadata

    @property
    def subject(self) -> str:
        if self.config and self.config.subject:
            return self.config.subject
        else:
            return self.header.subject or ''

    @property
    def summary(self) -> Text:
        """One line summary mostly for logging."""
        txt = self.summary_with_author

        if len(self.recipients) > 0:
            txt.append(', ').append(styled_key_value('recipients', self.recipients_txt()))

        return txt.append(CLOSE_PROPERTIES_CHAR)

    def __post_init__(self):
        self.filename = self.file_path.name
        self.file_id = extract_file_id(self.filename)

        # Special handling for copying properties out of the config for the document this one was extracted from
        if self.is_local_extract_file:
            self.url_slug = LOCAL_EXTRACT_REGEX.sub('', file_stem_for_id(self.file_id))
            extracted_from_doc_id = self.url_slug.split('_')[-1]

            if extracted_from_doc_id in ALL_FILE_CONFIGS:
                self._set_config_for_extracted_file(ALL_FILE_CONFIGS[extracted_from_doc_id])

        super().__post_init__()

        if self.config and self.config.recipients:
            self.recipients = self.config.recipients
        else:
            for recipient in self.header.recipients():
                self.recipients.extend(extract_emailer_names(recipient))

            # Assume mailing list emails are to Epstein
            if self.author in BCC_LISTS and (self.is_note_to_self or not self.recipients):
                self.recipients = [JEFFREY_EPSTEIN]

        self.recipients = uniquify(self.recipients)

        # Remove self CCs but preserve self emails
        if not (self.is_note_to_self or self.author is None):
            if self.author in self.recipients:
                self.log(f"Removing email to self for {self.author}")

            self.recipients = [r for r in self.recipients if r != self.author]

        self.recipients = sorted(list(set(self.recipients)), key=lambda r: r or UNKNOWN)
        self.text = self._prettify_text()
        self.actual_text = self._extract_actual_text()
        self.sent_from_device = self._sent_from_device()

    def is_from_or_to(self, name: str) -> bool:
        return name in [self.author] + self.recipients

    def recipients_txt(self, max_full_names: int = 2) -> Text:
        """Text object with comma separated colored versions of all recipients."""
        recipients = [r or UNKNOWN for r in self.recipients] if len(self.recipients) > 0 else [UNKNOWN]

        # Use just the last name for each recipient if there's 3 or more recipients
        return join_texts([
            Text(r if len(recipients) <= max_full_names else extract_last_name(r), style=get_style_for_name(r))
            for r in recipients
        ], join=', ')

    def _extract_actual_text(self) -> str:
        """The text that comes before likely quoted replies and forwards etc."""
        if self.config and self.config.actual_text is not None:
            return self.config.actual_text

        text = '\n'.join(self.text.split('\n')[self.header.num_header_rows:]).strip()

        if self.config and self.config.fwded_text_after:
            return text.split(self.config.fwded_text_after)[0].strip()
        elif self.header.num_header_rows == 0:
            return self.text

        self.log_top_lines(20, "Raw text:", logging.DEBUG)
        self.log(f"With {self.header.num_header_rows} header lines removed:\n{text[0:500]}\n\n", logging.DEBUG)
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

    def _extract_author(self) -> None:
        """Overloads superclass method, called at instantiation time."""
        self._extract_header()
        super()._extract_author()

        if not self.author and self.header.author:
            authors = extract_emailer_names(self.header.author)
            self.author = authors[0] if (len(authors) > 0 and authors[0]) else None

    def _extract_header(self) -> None:
        """Extract an `EmailHeader` from the OCR text."""
        header_match = EMAIL_SIMPLE_HEADER_REGEX.search(self.text)

        if header_match:
            self.header = EmailHeader.from_header_lines(header_match.group(0))

            # DOJ file OCR text is broken in a less consistent way than the HOUSE_OVERSIGHT files
            if self.header.is_empty() and not self.is_doj_file:
                self.header.repair_empty_header(self.lines)
        else:
            log_level = logging.INFO if self.config else logging.WARNING
            self.log_top_lines(msg='No email header match found!', level=log_level)
            self.header = EmailHeader(field_names=[])

        logger.debug(f"{self.file_id} extracted header\n\n{self.header}\n")

    def _extract_timestamp(self) -> datetime:
        """Find the time this email was sent."""
        if self.header.sent_at and (timestamp := _parse_timestamp(self.header.sent_at)):
            return timestamp

        searchable_lines = self.lines[0:MAX_NUM_HEADER_LINES]
        searchable_text = '\n'.join(searchable_lines)

        if (date_match := DATE_HEADER_REGEX.search(searchable_text)):
            if (timestamp := _parse_timestamp(date_match.group(1))):
                return timestamp

        logger.debug(f"Failed to find timestamp, falling back to parsing {MAX_NUM_HEADER_LINES} lines...")

        for line in searchable_lines:
            if not TIMESTAMP_LINE_REGEX.search(line):
                continue

            if (timestamp := _parse_timestamp(line)):
                logger.debug(f"Fell back to timestamp {timestamp} in line '{line}'...")
                return timestamp

        no_timestamp_msg = f"No timestamp found in '{self.file_path.name}'"

        if self.is_duplicate:
            logger.warning(f"{no_timestamp_msg} but timestamp should be copied from {self.duplicate_of_id}")
        else:
            logger.error(f"{no_timestamp_msg}, top lines:\n" + '\n'.join(self.lines[0:MAX_NUM_HEADER_LINES + 10]))

        return FALLBACK_TIMESTAMP

    def _idx_of_nth_quoted_reply(self, n: int = MAX_QUOTED_REPLIES) -> int | None:
        """Get position of the nth 'On June 12th, 1985 [SOMEONE] wrote:' style line in self.text."""
        header_offset = len(self.header.header_chars)
        text = self.text[header_offset:]

        for i, match in enumerate(QUOTED_REPLY_LINE_REGEX.finditer(text)):
            if i >= n:
                return match.end() + header_offset - 1

    def _merge_lines(self, idx1: int, idx2: int | None = None) -> None:
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

        self._set_computed_fields(lines=lines)

    def _prettify_text(self) -> str:
        """Add newlines before quoted replies and snip signatures."""
        # Insert line breaks now unless header is broken, in which case we'll do it later after fixing header
        text = self.text if self.header.was_initially_empty else _add_line_breaks(self.text)
        text = REPLY_REGEX.sub(r'\n\1', text)  # Newlines between quoted replies

        for name, signature_regex in EMAIL_SIGNATURE_REGEXES.items():
            signature_replacement = f'<...snipped {name.lower()} email signature...>'
            text, num_replaced = signature_regex.subn(signature_replacement, text)
            self.signature_substitution_counts[name] = self.signature_substitution_counts.get(name, 0)
            self.signature_substitution_counts[name] += num_replaced

        # Share / Tweet lines
        if self.author == KATHRYN_RUEMMLER:
            text = '\n'.join([line for line in text.split('\n') if line not in ['Share', 'Tweet', 'Bookmark it']])

        return collapse_newlines(text).strip()

    def _remove_line(self, idx: int) -> None:
        """Remove a line from self.lines."""
        num_lines = idx * 2
        self.log_top_lines(num_lines, msg=f'before removal of line {idx}')
        del self.lines[idx]
        self._set_computed_fields(lines=self.lines)
        self.log_top_lines(num_lines, msg=f'after removal of line {idx}')

    def _repair(self) -> None:
        """Repair particularly janky files. Note that OCR_REPAIRS are applied *after* other line adjustments."""
        if BAD_FIRST_LINE_REGEX.match(self.lines[0]):
            self._set_computed_fields(lines=self.lines[1:])

        self._set_computed_fields(lines=[line for line in self.lines if not BAD_LINE_REGEX.match(line)])
        old_text = self.text

        if self.file_id in LINE_REPAIR_MERGES:
            for merge_args in LINE_REPAIR_MERGES[self.file_id]:
                self._merge_lines(*merge_args)

        if self.file_id in ['025233']:
            self.lines[4] = f"Attachments: {self.lines[4]}"
            self._set_computed_fields(lines=self.lines)
        elif self.file_id == '029977':
            self._set_computed_fields(text=self.text.replace('Sent 9/28/2012 2:41:02 PM', 'Sent: 9/28/2012 2:41:02 PM'))

        # Bad line removal
        if self.file_id == '025041':
            self._remove_line(4)
            self._remove_line(4)
        elif self.file_id == '029692':
            self._remove_line(3)

        if old_text != self.text:
            self.log(f"Modified text, old:\n\n" + '\n'.join(old_text.split('\n')[0:12]) + '\n')
            self.log_top_lines(12, 'Result of modifications')

        repaired_text = self._repair_links_and_quoted_subjects(self.repair_ocr_text(OCR_REPAIRS, self.text))
        self._set_computed_fields(text=repaired_text)

    def _repair_links_and_quoted_subjects(self, text: str) -> str:
        """Repair links that the OCR has broken into multiple lines as well as 'Subject:' lines."""
        lines = text.split('\n')
        subject_line = next((line for line in lines if line.startswith('Subject:')), None) or ''
        subject = subject_line.split(':')[1].strip() if subject_line else ''
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if LINK_LINE_REGEX.search(line):
                while i < (len(lines) - 1) \
                        and not lines[i + 1].startswith('htt') \
                        and (lines[i + 1].endswith('/') \
                            or any(s in lines[i + 1] for s in URL_SIGNIFIERS) \
                            or LINK_LINE2_REGEX.match(lines[i + 1])):
                    logger.debug(f"{self.filename}: Joining link lines\n   1. {line}\n   2. {lines[i + 1]}\n")
                    line += lines[i + 1]
                    i += 1

                line = line.replace(' ', '')
            elif ' http' in line and line.endswith('html'):
                pre_link, post_link = line.split(' http', 1)
                line = f"{pre_link} http{post_link.replace(' ', '')}"
            elif line.startswith('Subject:') and i < (len(lines) - 2) and len(line) >= 40:
                next_line = lines[i + 1]
                next_next = lines[i + 2]

                if len(next_line) <= 1 or any([cont in next_line for cont in BAD_SUBJECT_CONTINUATIONS]):
                    pass
                elif (subject.endswith(next_line) and next_line != subject) \
                        or (FIELDS_COLON_REGEX.search(next_next) and not FIELDS_COLON_REGEX.search(next_line)):
                    self.log(f"Fixing broken subject line\n  line: '{line}'\n    next: '{next_line}'\n    next: '{next_next}'\nsubject='{subject}'\n")
                    line += f" {next_line}"
                    i += 1

            new_lines.append(line)
            i += 1

        logger.debug(f"----after line repair---\n" + '\n'.join(new_lines[0:20]) + "\n---")
        return '\n'.join(lines)

    def _sent_from_device(self) -> str | None:
        """Find any 'Sent from my iPhone' style signature line if it exist in the 'actual_text'."""
        if (sent_from_match := SENT_FROM_REGEX.search(self.actual_text)):
            sent_from = sent_from_match.group(0)
            return 'S' + sent_from[1:] if sent_from.startswith('sent') else sent_from

    def _set_config_for_extracted_file(self, extracted_from_doc_cfg: DocCfg) -> None:
        """Copy info from original config for file this document was extracted from."""
        if self.file_id in ALL_FILE_CONFIGS:
            self.config = cast(EmailCfg, deepcopy(ALL_FILE_CONFIGS[self.file_id]))
            self.log(f"Merging existing cfg for '{self.file_id}' with cfg for extracted document...")
        else:
            self.config = EmailCfg(id=self.file_id)

        if (extracted_from_description := extracted_from_doc_cfg.complete_description):
            extracted_description = f"{APPEARS_IN} {extracted_from_description}"

            if isinstance(extracted_from_doc_cfg, EmailCfg):
                extracted_description += ' email'

            if self.config_description:
                self.warn(f"Overwriting description '{self.config_description}' with extract's '{extracted_from_description}'")

            self.config.description = extracted_description

        self.config.is_interesting = self.config.is_interesting or extracted_from_doc_cfg.is_interesting
        self.log(f"Constructed synthetic config: {self.config}")

    def _truncate_to_length(self) -> int:
        """When printing truncate this email to this length."""
        quote_cutoff = self._idx_of_nth_quoted_reply()  # Trim if there's many quoted replies
        includes_truncate_term = next((term for term in TRUNCATE_TERMS if term in self.text), None)

        if args.whole_file:
            num_chars = len(self.text)
        elif args.truncate:
            num_chars = args.truncate
        elif self.config and self.config.truncate_to is not None:
            num_chars = len(self.text) if self.config.truncate_to == NO_TRUNCATE else self.config.truncate_to
        elif self.is_interesting:
            num_chars = len(self.text)
        elif self.author in TRUNCATE_EMAILS_FROM \
                or any([self.is_from_or_to(n) for n in TRUNCATE_EMAILS_FROM_OR_TO]) \
                or self.is_fwded_article \
                or includes_truncate_term:
            num_chars = min(quote_cutoff or MAX_CHARS_TO_PRINT, TRUNCATED_CHARS)
        else:
            if quote_cutoff and quote_cutoff < MAX_CHARS_TO_PRINT:
                trimmed_words = self.text[quote_cutoff:].split()

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
            else:
                num_chars = min(self.file_size, MAX_CHARS_TO_PRINT)

            # Always print whole email for 1st email for user
            if self._is_first_for_user and num_chars < self.file_size and not self.is_duplicate:
                logger.info(f"{self} Overriding cutoff {num_chars} for first email")
                num_chars = self.file_size

        log_args = {
            'num_chars': num_chars,
            '_is_first_for_user': self._is_first_for_user,
            'author_truncate': self.author in TRUNCATE_EMAILS_FROM,
            'is_fwded_article': self.is_fwded_article,
            'is_quote_cutoff': quote_cutoff == num_chars,
            'includes_truncate_term': json.dumps(includes_truncate_term) if includes_truncate_term else None,
            'quote_cutoff': quote_cutoff,
        }

        log_args_str = ', '.join([f"{k}={v}" for k, v in log_args.items() if v])
        logger.debug(f"Truncate determination: {log_args_str}")
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
            trim_footer_txt = self.truncation_note(num_chars)

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
            text = _add_line_breaks(text)
            self.rewritten_header_ids.add(self.file_id)

        lines = [
            Text.from_markup(f"[link={line}]{line}[/link]") if line.startswith('http') else Text(line)
            for line in text.split('\n')
        ]

        text = join_texts(lines, '\n')

        email_txt_panel = Panel(
            highlighter(text).append('...\n\n').append(trim_footer_txt) if trim_footer_txt else highlighter(text),
            border_style=self.border_style,
            expand=False,
            subtitle=REWRITTEN_HEADER_MSG if should_rewrite_header else None,
        )

        yield self.file_info_panel()
        yield Padding(email_txt_panel, (0, 0, 1, INFO_INDENT))

        if self.attached_docs:
            attachments_table_title = f" {self.url_slug} Email Attachments:"
            attachments_table = OtherFile.files_preview_table(self.attached_docs, title=attachments_table_title)
            yield Padding(attachments_table, (0, 0, 1, 12))

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
                link_text_obj(email.external_url, email.timestamp_without_seconds, style=link_style),
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
    return EMAIL_SIMPLE_HEADER_LINE_BREAK_REGEX.sub(r'\n\1\n', email_text).strip()


def _parse_timestamp(timestamp_str: str) -> None | datetime:
    try:
        if (american_date_match := AMERICAN_TIME_REGEX.search(timestamp_str)):
            timestamp_str = american_date_match.group(1)
        else:
            timestamp_str = timestamp_str.replace('(GMT-05:00)', 'EST')
            timestamp_str = BAD_TIMEZONE_REGEX.sub(' ', timestamp_str).strip()

        timestamp = parse(timestamp_str, fuzzy=True, tzinfos=TIMEZONE_INFO)
        logger.debug(f'Parsed timestamp "%s" from string "%s"', timestamp, timestamp_str)
        return remove_timezone(timestamp)
    except Exception as e:
        logger.debug(f'Failed to parse "{timestamp_str}" to timestamp!')
