from dateutil.parser import parse

from epstein_files.documents.documents.categories import (Category, Interesting, Neutral, Uninteresting,
     is_category, is_interesting, is_uninteresting)
from epstein_files.documents.documents.doc_cfg import DocCfg
from epstein_files.util.constant.names import *
from epstein_files.util.helpers.string_helper import has_line_starting_with
from epstein_files.util.logging import logger

# Inferred category config regexes
DEUTSCHE_SOUTHERN_REGEX = re.compile(r"^Deutsche Bank.*(SOUTHERN TRUST|RED HOOK QUARTER)", re.DOTALL)
EVIDENCE_REGEX = re.compile(r"^ITEM\s+WAS\s+NOT\s+SCANNED")
FBI_FILE_REGEX = re.compile(r"^(UNCLASSIFIED\s+)?FEDERAL BUREAU OF INVESTIGATION")
SUBPOENA_REGEX = re.compile(r"GRAND JURY SUBPOENA")
LEGAL_FILING_REGEX = re.compile(r"^Case (\d+:\d+-.*?) Doc")
SOUTHERN_FINANCIAL_REGEX = re.compile(r"^Southern Financial LLC salesforce.com")
VALAR_CAPITAL_CALL_REGEX = re.compile(r"^Valor .{,50} Capital Call", re.MULTILINE)
VI_DAILY_NEWS_REGEX = re.compile(r'virgin\s*is[kl][ai]nds\s*daily\s*news', re.IGNORECASE)


def build_cfg_from_text(text: str) -> DocCfg | None:
    """Scan the text to see if an author and description can be inferred."""
    lines = text.split('\n')
    cfg = None

    if FBI_FILE_REGEX.match(text):
        return _cfg(category=Neutral.LEGAL, author=FBI, description='memorandum or report')
    elif EVIDENCE_REGEX.match(text):
        return _cfg(category=Neutral.LEGAL, description='photos of collected evidence')
    elif SUBPOENA_REGEX.search(text):
        return _cfg(category=Neutral.LEGAL, description='grand jury subpoena or response')
    elif VI_DAILY_NEWS_REGEX.search(text):
        return _cfg(category=Uninteresting.ARTICLE, author=VI_DAILY_NEWS)
    elif has_line_starting_with(text, [VALAR_GLOBAL_FUND, VALAR_VENTURES.upper()], 2):
        return valar_cfg()
    elif SOUTHERN_FINANCIAL_REGEX.match(text):
        return _cfg(category=Interesting.MONEY, description="transactions by Epstein's Southern Financial LLC")
    elif DEUTSCHE_SOUTHERN_REGEX.match(text):
        return _cfg(category=Interesting.MONEY, description=f"{DEUTSCHE_BANK} statement for Epstein's Southern Trust Company")
    elif VALAR_CAPITAL_CALL_REGEX.search(text):
        return valar_cfg('requesting money previously promised by Epstein to invest in a new opportunity')
    elif (case_match := LEGAL_FILING_REGEX.search(text)):
        return _cfg(category=Neutral.LEGAL, description=f"legal filing in case {case_match.group(1)}")
    elif lines[0].lower() == 'valuation report':
        cfg = _cfg(category=Neutral.FINANCE, description="valuations of Epstein's investments", is_interesting=True)

        try:
            cfg.date = str(parse(lines[1]))
        except Exception as e:
            logger.warning(f"Failed to parse valuation report date from {lines[0:2]}")

        return cfg


def valar_cfg(description: str = '') -> DocCfg:
    return _cfg(
        category=Interesting.CRYPTO,  # TODO: not really crypto?
        author=VALAR_VENTURES,
        description=description or f"is a fintech focused {PETER_THIEL} fund Epstein was invested in",
    )


def _cfg(**kwargs) -> DocCfg:
    return DocCfg(id='', **kwargs)  # TODO: setting id='' sucks
