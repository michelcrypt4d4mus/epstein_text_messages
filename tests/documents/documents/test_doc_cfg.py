import pytest
from copy import deepcopy

from epstein_files.documents.documents.doc_cfg import DocCfg, EmailCfg
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import QUESTION_MARKS_TXT
from epstein_files.util.constant.names import BLOCKCHAIN_CAPITAL, BOFA_MERRILL, JOI_ITO, Name
from epstein_files.util.constant.strings import *

RANDOM_ID = '123456'


@pytest.fixture
def academia_doc() -> DocCfg:
    return _oversight_cfg(ACADEMIA)

@pytest.fixture
def attached_doc(junk_email_cfg) -> DocCfg:
    return _oversight_cfg(LEGAL, attached_to_email_id=junk_email_cfg.id)

@pytest.fixture
def blockchain_cap_cfg() -> DocCfg:
    return _oversight_cfg(CRYPTO, author=BLOCKCHAIN_CAPITAL, description="investor report")

@pytest.fixture
def book_cfg() -> DocCfg:
    return _oversight_cfg(BOOK, author='Elon Musk', description="Illmatic")

@pytest.fixture
def empty_doj_cfg() -> DocCfg:
    return _doj_cfg()

@pytest.fixture
def empty_house_cfg() -> DocCfg:
    return _oversight_cfg()

@pytest.fixture
def finance_report() -> DocCfg:
    return _oversight_cfg(FINANCE, author=BOFA_MERRILL, description="Grapes")

@pytest.fixture
def interesting_doc() -> DocCfg:
    cfg = _oversight_cfg(ACADEMIA)
    cfg.is_interesting = True
    return cfg

@pytest.fixture
def interesting_author() -> DocCfg:
    return _doj_cfg(ACADEMIA, author=JOI_ITO)

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
def skype_author() -> DocCfg:
    return _oversight_cfg(SKYPE_LOG, author='linkspirit')

@pytest.fixture
def skype_cfg() -> DocCfg:
    return _oversight_cfg(SKYPE_LOG)

@pytest.fixture
def tweet_cfg() -> DocCfg:
    return _doj_cfg(TWEET, author='Klippenstein')

@pytest.fixture
def uninteresting_description() -> DocCfg:
    return _doj_cfg(LEGAL, description=CVRA + " law stuff")


def test_category_txt(blockchain_cap_cfg, empty_house_cfg, junk_doc_cfg, legal_cfg, skype_cfg, skype_author):
    assert blockchain_cap_cfg.category_txt.style == 'orange1 bold'
    assert empty_house_cfg.category_txt == QUESTION_MARKS_TXT
    assert junk_doc_cfg.category_txt.plain == JUNK
    assert skype_cfg.category_txt.plain == SKYPE_LOG
    assert skype_cfg.category_txt.style == 'wheat4'
    assert legal_cfg.category_txt.style == 'purple'


def test_complete_description(
    attached_doc,
    blockchain_cap_cfg,
    book_cfg,
    empty_house_cfg,
    finance_report,
    harvard_poetry_cfg,
    junk_doc_cfg,
    junk_email_cfg,
    legal_cfg,
    skype_cfg,
    skype_author,
    tweet_cfg
):
    assert attached_doc.complete_description == f"legal, attached to email {junk_email_cfg.id}"
    assert blockchain_cap_cfg.complete_description == "Blockchain Capital investor report"
    assert book_cfg.complete_description == 'book titled "Illmatic" by Elon Musk'
    # Empty
    assert empty_house_cfg.complete_description == ''
    empty_house_cfg.attached_to_email_id = junk_email_cfg.id
    assert empty_house_cfg.complete_description == f"attached to email {junk_email_cfg.id}"
    # Finance
    assert finance_report.complete_description == f"{BOFA_MERRILL} report: Grapes"
    # Harvard
    assert harvard_poetry_cfg.complete_description == 'Harvard poetry stuff from Lisa New'
    # Junk
    assert junk_doc_cfg.complete_description == 'junk'
    junk_doc_cfg.description = 'junk mail'
    assert junk_doc_cfg.complete_description == 'junk mail'
    # Legal
    assert legal_cfg.complete_description == f"clinton v. trump: case law"
    # Skype no author
    assert skype_cfg.complete_description == SKYPE_LOG.lower()
    # Skype with author
    assert skype_author.complete_description == f"{SKYPE_LOG.lower()} of conversation with linkspirit"
    skype_author.description = 'something'
    assert skype_author.complete_description == f"{SKYPE_LOG.lower()} of conversation with linkspirit something"
    # Tweet
    assert tweet_cfg.complete_description == 'Tweet by Klippenstein'
    tweet_cfg.description = 'libelous'
    assert tweet_cfg.complete_description == 'Tweet by Klippenstein libelous'


def test_is_of_interest(
    academia_doc,
    blockchain_cap_cfg,
    empty_doj_cfg,
    empty_house_cfg,
    finance_report,
    harvard_poetry_cfg,
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
    assert empty_doj_cfg.is_of_interest is None
    assert empty_house_cfg.is_of_interest is True
    assert finance_report.is_of_interest is False
    assert harvard_poetry_cfg.is_of_interest is False
    assert interesting_author.is_of_interest is True
    assert interesting_doc.is_of_interest is True
    assert junk_doc_cfg.is_of_interest is False
    assert junk_email_cfg.is_of_interest is False
    assert legal_cfg.is_of_interest is True
    assert skype_cfg.is_of_interest is True
    assert uninteresting_description.is_of_interest is False



def test_books(epstein_files):
    book = epstein_files.get_id('010912', required_type=OtherFile)
    assert book.config.category == BOOK
    assert book.config.complete_description == "book titled '\"Free Growth and Other Surprises\" (draft)' by Gordon Getty"
    book = epstein_files.get_id('018438', required_type=OtherFile)
    assert book.config.category == BOOK
    assert book.config.complete_description == 'book titled "The S&M Feminist" by Clarisse Thorn'


def _oversight_cfg(category: str = '', **kwargs) -> DocCfg:
    return _doc_cfg('123456', category=category, **kwargs)


def _doj_cfg(category: str = '', **kwargs) -> DocCfg:
    return _doc_cfg('EFTA02614678', category=category, **kwargs)


def _doc_cfg(id: str, category: str = '', author: Name = None, **kwargs) -> DocCfg:
    return DocCfg(id=id, category=category, author=author, **kwargs)
