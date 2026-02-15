import pytest
from copy import deepcopy

from epstein_files.documents.documents.doc_cfg import DocCfg, EmailCfg
from epstein_files.output.highlight_config import QUESTION_MARKS_TXT
from epstein_files.util.constant.names import BLOCKCHAIN_CAPITAL, BOFA_MERRILL, JOI_ITO, Name
from epstein_files.util.constant.strings import *

RANDOM_ID = '123456'


@pytest.fixture
def academia_doc() -> DocCfg:
    return _oversight_cfg(ACADEMIA)


@pytest.fixture
def blockchain_cap_cfg() -> DocCfg:
    return _oversight_cfg(CRYPTO, author=BLOCKCHAIN_CAPITAL, description="investor report")


@pytest.fixture
def empty_cfg() -> DocCfg:
    return _doj_cfg()


@pytest.fixture
def interesting_doc() -> DocCfg:
    cfg = _oversight_cfg(ACADEMIA)
    cfg.is_interesting = True
    return cfg


@pytest.fixture
def interesting_author() -> DocCfg:
    return _doj_cfg(ACADEMIA, author=JOI_ITO)


@pytest.fixture
def uninteresting_description() -> DocCfg:
    return _doj_cfg(LEGAL, description=CVRA + " law stuff")


@pytest.fixture
def junk_doc_cfg() -> DocCfg:
    return _oversight_cfg(JUNK)


@pytest.fixture
def junk_email_cfg() -> EmailCfg:
    return EmailCfg(id=RANDOM_ID, category=JUNK, author='who knows')


@pytest.fixture
def legal_cfg() -> DocCfg:
    return _oversight_cfg(LEGAL, author='clinton v. trump', description='case law')


@pytest.fixture
def finance_report() -> DocCfg:
    return _oversight_cfg(FINANCE, author=BOFA_MERRILL, description="grapes")


@pytest.fixture
def skype_cfg() -> DocCfg:
    return _oversight_cfg(SKYPE_LOG)


@pytest.fixture
def skype_author() -> DocCfg:
    return _oversight_cfg(SKYPE_LOG, author='linkspirit')


def test_category_txt(empty_cfg, junk_doc_cfg, legal_cfg, skype_cfg, skype_author):
    print('running test_category_txt()')
    assert empty_cfg.category_txt == QUESTION_MARKS_TXT
    assert junk_doc_cfg.category_txt.plain == JUNK
    assert skype_cfg.category_txt.plain == SKYPE_LOG
    assert skype_cfg.category_txt.style == 'wheat4'
    assert legal_cfg.category_txt.style == 'purple'


def test_complete_description(blockchain_cap_cfg, finance_report, junk_doc_cfg, legal_cfg, skype_cfg, skype_author):
    assert legal_cfg.complete_description == f"clinton v. trump: case law"
    # Junk
    assert junk_doc_cfg.complete_description == 'junk'
    junk_doc_cfg.description = 'junk mail'
    assert junk_doc_cfg.complete_description == 'junk mail'
    # Skype
    assert skype_cfg.complete_description == SKYPE_LOG.lower()
    assert skype_author.complete_description == f"{SKYPE_LOG.lower()} of conversation with linkspirit"
    skype_author.description = 'something'
    assert skype_author.complete_description == f"{SKYPE_LOG.lower()} of conversation with linkspirit something"
    # Finance
    assert finance_report.complete_description == f"{BOFA_MERRILL} report: grapes"
    assert blockchain_cap_cfg.complete_description == "Blockchain Capital investor report"


def test_is_of_interest(
    academia_doc,
    blockchain_cap_cfg,
    finance_report,
    interesting_author,
    interesting_doc,
    junk_doc_cfg,
    junk_email_cfg,
    legal_cfg,
    skype_cfg,
    uninteresting_description
):
    assert academia_doc.is_of_interest is False
    assert blockchain_cap_cfg.is_of_interest is True
    assert finance_report.is_of_interest is False
    assert interesting_author.is_of_interest is True
    assert interesting_doc.is_of_interest is True
    assert junk_doc_cfg.is_of_interest is False
    assert junk_email_cfg.is_of_interest is False
    assert legal_cfg.is_of_interest is None
    assert skype_cfg.is_of_interest is True
    assert uninteresting_description.is_of_interest is False


def _oversight_cfg(category: str = '', **kwargs) -> DocCfg:
    return _doc_cfg('123456', category=category, **kwargs)


def _doj_cfg(category: str = '', **kwargs) -> DocCfg:
    return _doc_cfg('EFTA02614678', category=category, **kwargs)


def _doc_cfg(id: str, category: str = '', author: Name = None, **kwargs) -> DocCfg:
    return DocCfg(id=id, category=category, author=author, **kwargs)
