from dateutil.parser import parse

from epstein_files.documents.documents.categories import Category, Interesting, Neutral, Uninteresting
from epstein_files.documents.documents.doc_cfg import DocCfg
from epstein_files.util.constant.names import *
from epstein_files.util.helpers.string_helper import has_line_starting_with
from epstein_files.util.logging import logger

# Inferred category config regexes
DEUTSCHE_SOUTHERN_REGEX = re.compile(r"^.{,50}Deutsche Bank.{,1000}(SOUTHERN TRUST|RED HOOK QUARTER)", re.DOTALL)
EVIDENCE_REGEX = re.compile(r".{,1000}ITEM\s+WAS\s+NOT\s+SCANNED")
FBI_FILE_REGEX = re.compile(r"^(UNCLASSIFIED\s+)?FEDERAL BUREAU OF INVESTIGATION")
HARD_DRIVE_REGEX = re.compile(r"westerndigital|Gold SATA")
LEGAL_FILING_REGEX = re.compile(r"^Case (\d+:\d+-.*?) Doc")
LSJE_FORM_REGEX = re.compile(r".{,5}LSJE,\s+LLC.*Emergency\s+Contact\s+Form", re.DOTALL)
SOUTHERN_FINANCIAL_REGEX = re.compile(r"^Southern Financial LLC salesforce.com")
SUBPOENA_REGEX = re.compile(r"GRAND JURY SUBPOENA")
VALAR_CAPITAL_CALL_REGEX = re.compile(r"^Val[ao]r.{,190} Capital Call", re.MULTILINE | re.IGNORECASE | re.DOTALL)
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)

LEDGERX_MSG = 'LedgerX was later acquired by FTX for $298 million'

def build_cfg_from_text(doc: 'Document') -> DocCfg | None:
    """Scan the text to see if author, description, category, etc. can be derived from the contents."""
    text = doc.text
    lines = text.split('\n')
    cfg = None

    def _cfg(**kwargs) -> DocCfg:
        return DocCfg(id=doc.file_id, **kwargs)  # TODO: setting id to nothing sucks

    if FBI_FILE_REGEX.search(text):
        return _cfg(category=Neutral.LEGAL, author=FBI, description='memorandum or report')
    elif EVIDENCE_REGEX.search(text):
        return _cfg(category=Neutral.LEGAL, description='photos of collected evidence')
    elif 'LedgerX' in text[0:500]:
        return _cfg(category=Interesting.CRYPTO, description=LEDGERX_MSG)
    elif LSJE_FORM_REGEX.search(text):
        return _cfg(category=Neutral.BUSINESS, description="emergency contact form for employee of Epstein's LSJE")
    elif SUBPOENA_REGEX.search(text):
        return _cfg(category=Neutral.LEGAL, description='grand jury subpoena or response')
    elif VI_DAILY_NEWS_REGEX.search(text):
        return _cfg(category=Uninteresting.ARTICLE, author=VI_DAILY_NEWS)
    elif has_line_starting_with(text, [VALAR_GLOBAL_FUND, VALAR_VENTURES.upper()], 2):
        return valar_cfg(doc.file_id, text=text)
    elif SOUTHERN_FINANCIAL_REGEX.match(text):
        return _cfg(category=Interesting.MONEY, description="transactions by Epstein's Southern Financial LLC")
    elif DEUTSCHE_SOUTHERN_REGEX.match(text):
        return _cfg(category=Interesting.MONEY, description=f"{DEUTSCHE_BANK} statement for Epstein's Southern Trust Company")
    elif VALAR_CAPITAL_CALL_REGEX.search(text):
        return valar_cfg(doc.file_id, 'requesting money previously promised by Epstein to invest in a new opportunity')
    elif (case_match := LEGAL_FILING_REGEX.search(text)):
        return _cfg(category=Neutral.LEGAL, description=f"legal filing in case {case_match.group(1)}")
    elif len(text) < 2600 and HARD_DRIVE_REGEX.search(text):
        return _cfg(category=Neutral.MISC, description='photo of a hard drive')
    elif lines[0].lower().strip() == 'valuation report':
        cfg = _cfg(category=Interesting.MONEY, description="valuations of Epstein's investments", is_interesting=True)

        try:
            cfg.date = str(parse(lines[1]))
        except Exception as e:
            logger.warning(f"Failed to parse valuation report date for derived DocCfg from {lines[0:2]}")

        return cfg


def valar_cfg(id: str, description: str = '', text: str = '') -> DocCfg:
    return DocCfg(
        id=id,
        category=Interesting.CRYPTO,  # TODO: not really crypto?
        author=VALAR_VENTURES,
        date='2015-06-30' if '6/30/2015' in text else '',
        description=description or f"is a fintech focused {PETER_THIEL} fund Epstein was invested in",
    )
