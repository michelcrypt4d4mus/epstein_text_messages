"""
Methods to help with building various kinds of `DocCfg` or `EmailCfg` objects.
"""
from datetime import date
from dateutil.parser import parse
from typing import TypeVar

from epstein_files.documents.documents.categories import Category, Interesting, Neutral, Uninteresting
from epstein_files.documents.config.communication_cfg import CommunicationCfg, Platform
from epstein_files.documents.config.doc_cfg import DocCfg
from epstein_files.people.names import *
from epstein_files.util.helpers.string_helper import as_pattern, has_line_starting_with, join_truthy
from epstein_files.util.logging import logger

# Inferred category config regexes
DEUTSCHE_SOUTHERN_REGEX = re.compile(r"^.{,50}Deutsche Bank.{,1000}(SOUTHERN TRUST|RED HOOK QUARTER)", re.DOTALL)
EVIDENCE_REGEX = re.compile(r".{,1000}ITEM\s+WAS\s+NOT\s+SCANNED")
FBI_FILE_REGEX = re.compile(r"^(UNCLASSIFIED\s+)?FEDERAL BUREAU OF INVESTIGATION")
FILED_DATE_REGEX = re.compile(r"(?:Docket|Filed) (\d{2})/(\d{2})/(\d{2,4})")
GRAND_JURY_REGEX = re.compile(r"Grand Jury", re.IGNORECASE)
HARD_DRIVE_REGEX = re.compile(r"westerndigital|Gold SATA")
LEGAL_FILING_REGEX = re.compile(r"^Case (\d+:\d+-.*?)\s+Doc")
LSJE_FORM_REGEX = re.compile(r".{,5}LSJE,\s+LLC.*Emergency\s+Contact\s+Form", re.DOTALL)
SOUTHERN_FINANCIAL_REGEX = re.compile(r"^Southern Financial LLC salesforce.com")
SUBPOENA_REGEX = re.compile(r"GRAND JURY SUBPOENA")
VALAR_CAPITAL_CALL_REGEX = re.compile(r"^Val[ao]r.{,190} Capital Call", re.MULTILINE | re.IGNORECASE | re.DOTALL)
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)

EPSTEIN_INVESTIGATION = 'Epstein investigation'
GIUFFRE_V_MAXWELL = f"{VIRGINIA_GIUFFRE} v. {GHISLAINE_MAXWELL}"
JANE_DOE_101_V_EPSTEIN = f"{JANE_DOE} 101 v. Epstein"
JANE_DOE_2_V_EPSTEIN = f'Jane Doe #2 v. {JEFFREY_EPSTEIN}'
JANE_DOE_V_USA = 'Jane Doe #1 and Jane Doe #2 v. United States'
LEDGERX_MSG = 'LedgerX was later acquired by FTX for $298 million'
WOLFF_EPSTEIN_ARTICLE_DRAFT = f"draft of an unpublished article ca. 2014"

# Don't join with "about" if the note starts with one of these words
REPORT_ABOUT_PREFIXES = [
    'contain',
    # 'with',
]

DUPLICATES = {
    'EFTA00811539': ['EFTA00599617'],
    'EFTA00591792': ['EFTA00810358'],
}

CASE_IDS = {
    '1:19-cv-10479-ALC-DCF': f"Juliette Bryant v. {DARREN_INDYKE} and {RICHARD_KAHN} as executors of Epstein Estate",
    '1:20-cr-00330-AJN': f"US v. {GHISLAINE_MAXWELL}",
    '1:20-cv-00833-PAE': f"New York Times v. {BUREAU_OF_PRISONS}",
    '1:19-cr-00490-RMB': f"US v. {JEFFREY_EPSTEIN}",
    '1:22-cv-10904-JSR': f"US Virgin Islands v. JPMorgan Chase",
    '9:08-cv-80736-KAM': JANE_DOE_V_USA,
    '9:09-cv-80656-KAM': JANE_DOE_2_V_EPSTEIN,
    '1:15-cv-07433-RWS': GIUFFRE_V_MAXWELL,  # TODO: this could be edwards v. dersh
    '9:09-cv-80591-KAM': JANE_DOE_101_V_EPSTEIN,
}

FILING_DATES = {
    'EFTA00145666': '2023-04-12',
    'EFTA00804328': '2016-02-10',
    'EFTA00081180': '2015-01-21',
    'EFTA00313650': '2017-01-26',
    'EFTA00210921': '2009-05-04',
}

FILING_TYPES = {
    'EFTA00212929': 'Complaint',
    'EFTA00221567': 'Amended Complaint'
}

EMERGENCY_CONTACT_DATES = {
    'EFTA00003042': '2019-02-06',
    'EFTA00003060': '2018-03-19',
}

DESCRIPTIONS = {
    'EFTA00015532': "alleging Epstein tried to buy victim's silence",
}

Cfg = TypeVar('Cfg', bound=DocCfg)


def us_versus_regex(name: str) -> re.Pattern:
    """Build pattern for e.g. 'U.S. v. Ghislaine Maxwell' detection."""
    first_name = extract_first_name(name)
    last_name = extract_last_name(name)
    pattern = fr"United States( of America)?( -?v-?\.?)?.{{,40}}({first_name} )?{last_name}"
    pattern = as_pattern(pattern)
    # logger.debug(f"{name}: '{pattern}'")
    return re.compile(pattern, re.IGNORECASE | re.DOTALL)


PROSECUTION_REGEXES = {
    f"U.S. v. {name}": us_versus_regex(name)
    for name in [GHISLAINE_MAXWELL, JEFFREY_EPSTEIN]
}


def build_cfg_from_text(doc: 'Document') -> DocCfg | None:
    """Scan the text to see if author, note, category, etc. can be derived from the contents."""
    text = doc.text
    lines = text.split('\n')
    cfg = None

    def _cfg(**kwargs) -> DocCfg:
        return DocCfg(id=doc.file_id, **kwargs)  # TODO: setting id to nothing sucks

    if FBI_FILE_REGEX.search(text):
        cfg = fbi_doc(doc.file_id)
    elif EVIDENCE_REGEX.search(text):
        cfg = _cfg(category=Neutral.LEGAL, note='photos of collected evidence')
    elif GRAND_JURY_REGEX.search(text[0:100]):
        case_matched = ''

        for case_name, regex in PROSECUTION_REGEXES.items():
            if regex.search(doc.text):
                case_matched = case_name
                break

        cfg = grand_jury(doc.file_id, case_matched)
    elif 'LedgerX' in text[0:500]:
        cfg = _cfg(category=Interesting.CRYPTO, note=LEDGERX_MSG)
    elif LSJE_FORM_REGEX.search(text):
        cfg = _cfg(
            category=Neutral.BUSINESS,
            date=EMERGENCY_CONTACT_DATES.get(doc.file_id, ''),
            note="emergency contact form for employee of Epstein's LSJE",
        )
    elif SUBPOENA_REGEX.search(text):
        cfg = _cfg(category=Neutral.LEGAL, note='grand jury subpoena or response')
    elif VI_DAILY_NEWS_REGEX.search(text):
        cfg = _cfg(category=Uninteresting.ARTICLE, author=VI_DAILY_NEWS)
    elif has_line_starting_with(text, [VALAR_GLOBAL_FUND, VALAR_VENTURES.upper()], 2):
        cfg = valar_cfg(doc.file_id, text=text)
    elif DEUTSCHE_SOUTHERN_REGEX.match(text):
        cfg = _cfg(
            author=DEUTSCHE_BANK,
            category=Interesting.MONEY,
            note=f"statement for Epstein's Southern Trust Company",
        )
    elif SOUTHERN_FINANCIAL_REGEX.match(text):
        cfg = _cfg(category=Interesting.MONEY, note="transactions by Epstein's Southern Financial LLC")
    elif VALAR_CAPITAL_CALL_REGEX.search(text):
        cfg = valar_cfg(doc.file_id, 'requesting money previously promised by Epstein to invest in a new opportunity')
    elif (case_match := LEGAL_FILING_REGEX.search(text)):
        case_name = CASE_IDS.get(case_match.group(1), f"case {case_match.group(1)}")
        filing_type = FILING_TYPES.get(doc.file_id, 'legal filing')
        note = join_truthy(f"{filing_type} in {case_name}", DESCRIPTIONS.get(doc.file_id, ''))
        cfg = _cfg(category=Neutral.LEGAL, note=note, date=FILING_DATES.get(doc.file_id, ''))

        if (filed_match := FILED_DATE_REGEX.search(text[:1000])):
            if len((year := filed_match.group(3))) == 2:
                year = f"20{year}"
            elif len(year) == 3:
                raise ValueError(f"year is only 3 chars long {filed_match}")

            cfg.date = f"{year}-{filed_match.group(1)}-{filed_match.group(2)}"
    elif len(text) < 2600 and HARD_DRIVE_REGEX.search(text):
        cfg = _cfg(category=Neutral.MISC, note='photo of a hard drive')
    elif lines[0].lower().strip() == 'valuation report':
        cfg = _cfg(category=Interesting.MONEY, note="valuations of Epstein's investments", is_interesting=True)

        try:
            cfg.date = str(parse(lines[1]))
        except Exception as e:
            logger.warning(f"Failed to parse valuation report date for derived DocCfg from {lines[0:2]}")

    if cfg:
        cfg.duplicate_ids = DUPLICATES.get(cfg.id, [])

    return cfg


def fbi_doc(id: str, note: str = EPSTEIN_INVESTIGATION, **kwargs) -> DocCfg:
    joiner = ', ' if any(note.startswith(word) for word in REPORT_ABOUT_PREFIXES) else ' about '
    note = join_truthy('report', note, joiner)
    return DocCfg(id=id, author=FBI, note=note, **kwargs)


def fedex_invoice(id: str, date: str, **kwargs) -> DocCfg:
    return DocCfg(id=id, author='FedEx', date=date, display_text='invoice', **kwargs)


def grand_jury(id: str, case_name: str = '', note: str = '', **kwargs) -> DocCfg:
    note_pfx = join_truthy('grand jury proceedings', case_name, ' in ')
    return DocCfg(id=id, category=Neutral.LEGAL, note=join_truthy(note_pfx, note), **kwargs)


def important_messages_pad(id: str, date: str = '') -> DocCfg:
    display_text = '"Important Message" formatted notepad with notes about missed phone calls etc.'
    return DocCfg(id=id, date=date, display_text=display_text)


def interview(id: str, author: str, interviewee: Name, note: str = '', **kwargs) -> CommunicationCfg:
    note = join_truthy(f"interview of {interviewee or UNKNOWN}", note, ', ')
    return CommunicationCfg(id=id, author=author, note=note, recipients=[interviewee], **kwargs)


def inventory(id: str, container: str, note: str = '', **kwargs) -> DocCfg:
    container = f"inventory of the contents of {container}"
    return DocCfg(id=id, note=join_truthy(container, note, ', includes '), **kwargs)


def letter(id: str, author: Name = None, recipients: list[Name] | None = None, note: str = '', date: str = '', **kwargs) -> CommunicationCfg:
    return CommunicationCfg(
        id=id,
        author=author,
        date=date,
        note=note,
        platform=Platform.LETTER,
        recipients=recipients or [],
        **kwargs
    )


def memo(id: str, author: str, note: str, date: str = '', **kwargs) -> DocCfg:
    return DocCfg(id=id, author=author, date=date, note=join_truthy("memo", note, ' about '), **kwargs)


def passenger_manifest(id: str, date: str, showing: str = '', **kwargs) -> DocCfg:
    return DocCfg(
        id=id,
        author=JEGE_INC,
        date=date,
        note=join_truthy("flight manifest", showing, ' showing '),
        show_full_panel=True,
        **kwargs
    )


def phone_bill_cfg(id: str, author: str, dates: str = '', **kwargs) -> DocCfg:
    return DocCfg(
        id=id,
        author=author,
        category=Uninteresting.PHONE_BILL,
        display_text=f"phone bill" + (f" covering {dates}" if dates else ''),
        **kwargs
    )


def press_release(id: str, author: Name, date: str = '', note: str = '', **kwargs) -> DocCfg:
    return DocCfg(id=id, author=author, category=Neutral.PRESSER, date=date, note=note, **kwargs)


def valar_cfg(id: str, note: str = '', text: str = '') -> DocCfg:
    return DocCfg(
        id=id,
        author=VALAR_VENTURES,
        category=Interesting.CRYPTO,  # TODO: not really crypto?
        date='2015-06-30' if '6/30/2015' in text else '',
        note=note or f"is a fintech focused {PETER_THIEL} fund Epstein was invested in",
    )


def wolff_draft_cfg(id: str, suffix: str = '', **kwargs) -> DocCfg:
    return DocCfg(
        id=id,
        author=MICHAEL_WOLFF,
        date='2014-08-31' if 'show_with_name' in kwargs else '2014-09-01',  # Very approximate, make excerpt show first
        note=join_truthy(WOLFF_EPSTEIN_ARTICLE_DRAFT, suffix),
        **kwargs
    )
