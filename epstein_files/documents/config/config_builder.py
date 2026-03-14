"""
Methods to help with building various kinds of `DocCfg` or `EmailCfg` objects.
"""
from dateutil.parser import parse
from typing import TypeVar

from epstein_files.documents.documents.categories import Category, Interesting, Neutral, Uninteresting
from epstein_files.documents.config.doc_cfg import CommunicationCfg, DocCfg, DuplicateType, EmailCfg
from epstein_files.people.names import *
from epstein_files.util.helpers.string_helper import has_line_starting_with, join_truthy
from epstein_files.util.logging import logger

# Inferred category config regexes
DEUTSCHE_SOUTHERN_REGEX = re.compile(r"^.{,50}Deutsche Bank.{,1000}(SOUTHERN TRUST|RED HOOK QUARTER)", re.DOTALL)
EVIDENCE_REGEX = re.compile(r".{,1000}ITEM\s+WAS\s+NOT\s+SCANNED")
FBI_FILE_REGEX = re.compile(r"^(UNCLASSIFIED\s+)?FEDERAL BUREAU OF INVESTIGATION")
GRAND_JURY_REGEX = re.compile(r"Grand Jury", re.IGNORECASE)
HARD_DRIVE_REGEX = re.compile(r"westerndigital|Gold SATA")
LEGAL_FILING_REGEX = re.compile(r"^Case (\d+:\d+-.*?)\s+Doc")
LSJE_FORM_REGEX = re.compile(r".{,5}LSJE,\s+LLC.*Emergency\s+Contact\s+Form", re.DOTALL)
SOUTHERN_FINANCIAL_REGEX = re.compile(r"^Southern Financial LLC salesforce.com")
SUBPOENA_REGEX = re.compile(r"GRAND JURY SUBPOENA")
VALAR_CAPITAL_CALL_REGEX = re.compile(r"^Val[ao]r.{,190} Capital Call", re.MULTILINE | re.IGNORECASE | re.DOTALL)
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)

EPSTEIN_INVESTIGATION = 'Epstein investigation'
JANE_DOE_V_USA = 'Jane Doe #1 and Jane Doe #2 v. United States'
LEDGERX_MSG = 'LedgerX was later acquired by FTX for $298 million'
WOLFF_EPSTEIN_ARTICLE_DRAFT = f"draft of an unpublished article ca. 2014"

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
}

EMERGENCY_CONTACT_DATES = {
    'EFTA00003042': '2019-02-06'
}

DESCRIPTIONS = {
    'EFTA00015532': "alleging Epstein tried to buy victim's silence",
}

# Don't join with "about" if the description starts with one of these words
REPORT_ABOUT_PREFIXES = [
    'contain',
    # 'with',
]

Cfg = TypeVar('Cfg', bound=DocCfg)


def build_cfg_from_text(doc: 'Document') -> DocCfg | None:
    """Scan the text to see if author, description, category, etc. can be derived from the contents."""
    text = doc.text
    lines = text.split('\n')
    cfg = None

    def _cfg(**kwargs) -> DocCfg:
        return DocCfg(id=doc.file_id, **kwargs)  # TODO: setting id to nothing sucks

    if FBI_FILE_REGEX.search(text):
        cfg = fbi_report(doc.file_id)
    elif EVIDENCE_REGEX.search(text):
        cfg = _cfg(category=Neutral.LEGAL, description='photos of collected evidence')
    elif GRAND_JURY_REGEX.search(text[0:100]):
        cfg = _cfg(category=Neutral.LEGAL, description='grand jury proceedings')
    elif 'LedgerX' in text[0:500]:
        cfg = _cfg(category=Interesting.CRYPTO, description=LEDGERX_MSG)
    elif LSJE_FORM_REGEX.search(text):
        cfg = _cfg(
            category=Neutral.BUSINESS,
            date=EMERGENCY_CONTACT_DATES.get(doc.file_id, ''),
            description="emergency contact form for employee of Epstein's LSJE",
        )
    elif SUBPOENA_REGEX.search(text):
        cfg = _cfg(category=Neutral.LEGAL, description='grand jury subpoena or response')
    elif VI_DAILY_NEWS_REGEX.search(text):
        cfg = _cfg(category=Uninteresting.ARTICLE, author=VI_DAILY_NEWS)
    elif has_line_starting_with(text, [VALAR_GLOBAL_FUND, VALAR_VENTURES.upper()], 2):
        cfg = valar_cfg(doc.file_id, text=text)
    elif SOUTHERN_FINANCIAL_REGEX.match(text):
        cfg = _cfg(category=Interesting.MONEY, description="transactions by Epstein's Southern Financial LLC")
    elif DEUTSCHE_SOUTHERN_REGEX.match(text):
        cfg = _cfg(category=Interesting.MONEY, description=f"{DEUTSCHE_BANK} statement for Epstein's Southern Trust Company")
    elif VALAR_CAPITAL_CALL_REGEX.search(text):
        cfg = valar_cfg(doc.file_id, 'requesting money previously promised by Epstein to invest in a new opportunity')
    elif (case_match := LEGAL_FILING_REGEX.search(text)):
        case_name = CASE_IDS.get(case_match.group(1), f"case {case_match.group(1)}")
        description = join_truthy(f"legal filing in {case_name}", DESCRIPTIONS.get(doc.file_id, ''))
        cfg = _cfg(category=Neutral.LEGAL, description=description)
    elif len(text) < 2600 and HARD_DRIVE_REGEX.search(text):
        cfg = _cfg(category=Neutral.MISC, description='photo of a hard drive')
    elif lines[0].lower().strip() == 'valuation report':
        cfg = _cfg(category=Interesting.MONEY, description="valuations of Epstein's investments", is_interesting=True)

        try:
            cfg.date = str(parse(lines[1]))
        except Exception as e:
            logger.warning(f"Failed to parse valuation report date for derived DocCfg from {lines[0:2]}")

    if cfg:
        cfg.duplicate_ids = DUPLICATES.get(cfg.id, [])

    return cfg


def binant_redacted(id: str, truncate_to: int = 700) -> EmailCfg:
    return EmailCfg(id=id, truncate_to=truncate_to, description=f"redacted discussion of art advisor {ETIENNE_BINANT}")


def blaine_letter(id: str, date: str, suffix: str = '', **kwargs) -> CommunicationCfg:
    return immigration_letter(
        id,
        DAVID_BLAINE,
        date=date,
        description=join_truthy(f"recommending genius visa for a Epstein's assistant {SVETLANA_POZHIDAEVA}", suffix),
        show_with_name=SVETLANA_POZHIDAEVA,
        **kwargs
    )


def fbi_defense_witness(id: str, witness: Name, date: str = '') -> DocCfg:
    description = f'Research and Key Findings for {witness or UNKNOWN}, defense witness for {GHISLAINE_MAXWELL}'
    return _set_fbi_doc_fields(DocCfg(id=id, date=date, description=description))


def fbi_interview(id: str, interviewee: Name, description: str = '', date: str = '', **kwargs) -> CommunicationCfg:
    description = join_truthy(f"interview with {interviewee or UNKNOWN}", description, ', ')
    cfg = CommunicationCfg(id=id, date=date, description=description, recipients=[interviewee], **kwargs)
    return _set_fbi_doc_fields(cfg)


def fbi_report(id: str, description: str = EPSTEIN_INVESTIGATION, **kwargs) -> DocCfg:
    joiner = ', ' if any(description.startswith(word) for word in REPORT_ABOUT_PREFIXES) else ' about '
    description = join_truthy('report', description, joiner)
    return _set_fbi_doc_fields(DocCfg(id=id, description=description, **kwargs))


def fbi_tip(id: str, about: str, **kwargs) -> DocCfg:
    return _set_fbi_doc_fields(DocCfg(id=id, description=f"tip {about}", **kwargs))


def fedex_invoice(id: str, date: str) -> DocCfg:
    return DocCfg(id=id, author='FedEx', date=date, display_text='FedEx invoice')


def immigration_letter(id: str, author: Name, date: str = '', description: str = '', show_with_name = '', **kwargs) -> CommunicationCfg:
    """`show_with_name` is who the letter is about."""
    person_recommended_for_visa = show_with_name or 'someone'
    suffix = f"recommending \"genius\" visa for {person_recommended_for_visa}"

    if person_recommended_for_visa not in description:
        description = join_truthy(description, suffix)

    return letter(
        id,
        author=author,
        date=date,
        description=description,
        is_interesting=True,
        recipients=['INS'],
        show_with_name=show_with_name,
        **kwargs
    )


def important_messages_pad(id: str, date: str = '') -> DocCfg:
    return DocCfg(
        id=id,
        date=date,
        display_text='"Important Message" formatted notepad with notes about missed phone calls etc.'
    )


def letter(id: str, author: Name, recipients: list[Name], description: str, date: str = '', **kwargs) -> CommunicationCfg:
    return CommunicationCfg(
        id=id,
        author=author,
        category=Category.LETTER,
        date=date,
        description=description,
        recipients=recipients,
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


def shaher_murder_email(id: str, description: str = '', **kwargs) -> EmailCfg:
    return EmailCfg(
        id=id,
        description=join_truthy(description, f"discussion of the murder of Martine Vik Magnussen by {SHAHER_ABDULHAK_BESHER}'s son Farouk"),
        is_interesting=True,
        **kwargs
    )


def starr_letter(id: str, date: str, duplicate_ids: list[str], dupe_type: DuplicateType = 'same', **kwargs) -> CommunicationCfg:
    return letter(
        id=id,
        author=KEN_STARR,
        date=date,
        description="requesting lenient treatment for Epstein",
        duplicate_ids=duplicate_ids,
        dupe_type=dupe_type,
        recipients=['Judge Mark Filip'],
        **kwargs
    )


def valar_cfg(id: str, description: str = '', text: str = '') -> DocCfg:
    return DocCfg(
        id=id,
        category=Interesting.CRYPTO,  # TODO: not really crypto?
        author=VALAR_VENTURES,
        date='2015-06-30' if '6/30/2015' in text else '',
        description=description or f"is a fintech focused {PETER_THIEL} fund Epstein was invested in",
    )


def victim_diary(id: str, description: str) -> DocCfg:
    return DocCfg(id=id, category=Interesting.DIARY, description=description)


def whistleblower_cfg(id, description: str = '') -> EmailCfg:
    return EmailCfg(
        id=id,
        description=join_truthy('SEC whistleblower email', description, ', '),
        is_interesting=True,
    )


def wolff_draft_cfg(id: str, suffix: str = '', **kwargs) -> DocCfg:
    return DocCfg(
        id=id,
        author=MICHAEL_WOLFF,
        date='2014-08-31' if 'show_with_name' in kwargs else '2014-09-01',  # Very approximate, make excerpt show first
        description=join_truthy(WOLFF_EPSTEIN_ARTICLE_DRAFT, suffix),
        **kwargs
    )


def _set_fbi_doc_fields(cfg: Cfg) -> Cfg:
    """Mutate `cfg` to set FBI related properties. Returns `cfg` argument for convenience."""
    cfg.author = FBI
    cfg.category = Neutral.GOVERNMENT
    return cfg
