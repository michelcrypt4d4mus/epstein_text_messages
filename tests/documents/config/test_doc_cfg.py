import pytest
from copy import deepcopy

from rich.text import Text

from epstein_files.documents.documents.categories import Interesting, Neutral, Uninteresting
from epstein_files.documents.config.communication_cfg import CommunicationCfg, Platform
from epstein_files.documents.config.doc_cfg import QUOTE_PREFIX, DocCfg
from epstein_files.documents.config.email_cfg import EmailCfg
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.highlight_config import QUESTION_MARKS_TXT
from epstein_files.people.names import *
from epstein_files.util.constant.strings import *
from epstein_files.util.constants import CONFIGS_BY_ID

ID = '123456'
SKYPE_LOG = 'Skype log'

BASE_TRUTHY_PROPS = {
    'is_displayed_as_img': False,
    'is_note_in_subheader': True,
    'is_valid_for_name_scan': True,
}


@pytest.fixture
def academia_cfg() -> DocCfg:
    return _oversight_cfg(Uninteresting.ACADEMIA)

@pytest.fixture
def attached_doc(junk_email_cfg) -> DocCfg:
    return _oversight_cfg(Neutral.LEGAL, attached_to_email_id=junk_email_cfg.id)

@pytest.fixture
def blockchain_cap_cfg() -> DocCfg:
    return _oversight_cfg(Interesting.CRYPTO, author=BLOCKCHAIN_CAPITAL, note="investor report")

@pytest.fixture
def book_cfg() -> DocCfg:
    return _oversight_cfg(Uninteresting.BOOK, author='Elon Musk', note="Illmatic")

@pytest.fixture
def dummy_cfg() -> DocCfg:
    return OtherFile.dummy_cfg()

@pytest.fixture
def empty_doj_cfg() -> DocCfg:
    return _doj_cfg()

@pytest.fixture
def empty_house_cfg() -> DocCfg:
    return _oversight_cfg()

@pytest.fixture
def finance_report() -> DocCfg:
    return _oversight_cfg(Neutral.FINANCE, author=BOFA_MERRILL, note="Grapes")

@pytest.fixture
def fwded_article() -> EmailCfg:
    return EmailCfg(id='123456', author=BOFA_MERRILL, is_fwded_article=True)

@pytest.fixture
def interesting_doc() -> DocCfg:
    cfg = _oversight_cfg(Uninteresting.ACADEMIA)
    cfg.is_interesting = True
    return cfg

@pytest.fixture
def junk_doc_cfg() -> DocCfg:
    return _oversight_cfg(Uninteresting.JUNK)

@pytest.fixture
def junk_email_cfg() -> EmailCfg:
    return EmailCfg(id=ID, category=Uninteresting.JUNK, author='who knows')

@pytest.fixture
def legal_cfg() -> DocCfg:
    return _oversight_cfg(Neutral.LEGAL, author='clinton v. trump', note='case law')

@pytest.fixture
def skype_author(skype_cfg) -> CommunicationCfg:
    cfg = deepcopy(skype_cfg)
    cfg.author='linkspirit'
    return cfg

@pytest.fixture
def skype_cfg() -> CommunicationCfg:
    return CommunicationCfg(id=ID, platform=Platform.SKYPE)

@pytest.fixture
def skype_recipients(skype_cfg) -> CommunicationCfg:
    cfg = deepcopy(skype_cfg)
    cfg.recipients = ['LBJ', 'JFK']
    return cfg

@pytest.fixture
def tweet_cfg() -> DocCfg:
    return _doj_cfg(Uninteresting.TWEET, author='Klippenstein')

@pytest.fixture
def UN_cfg() -> DocCfg:
    return CONFIGS_BY_ID['024185']

@pytest.fixture
def uninteresting_description() -> DocCfg:
    return _doj_cfg(Neutral.LEGAL, note=CVRA + " law stuff")

@pytest.fixture
def very_interesting_cfg(legal_cfg) -> DocCfg:
    cfg = deepcopy(legal_cfg)
    cfg.is_interesting = 10
    return cfg

@pytest.fixture
def whatsapp_cfg() -> CommunicationCfg:
    return CONFIGS_BY_ID['EFTA01613762']


def test_category_txt(blockchain_cap_cfg, empty_house_cfg, junk_doc_cfg, legal_cfg, skype_cfg):
    assert blockchain_cap_cfg.category_txt.style == 'orange1 bold'
    assert empty_house_cfg.category_txt == QUESTION_MARKS_TXT
    assert junk_doc_cfg.category_txt.plain == Uninteresting.JUNK
    assert skype_cfg.category_txt.plain == 'skype'
    assert skype_cfg.category_txt.style == 'bright_cyan'
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
    skype_recipients,
    tweet_cfg,
    whatsapp_cfg
):
    assert attached_doc.complete_description == f"attached to email {junk_email_cfg.id}"
    assert blockchain_cap_cfg.complete_description == "Blockchain Capital investor report"
    assert book_cfg.complete_description == 'book titled "Illmatic" by Elon Musk'
    # Empty
    assert empty_house_cfg.complete_description == ''
    empty_house_cfg.attached_to_email_id = junk_email_cfg.id
    assert empty_house_cfg.complete_description == f"attached to email {junk_email_cfg.id}"
    # Finance
    assert finance_report.complete_description == f"{BOFA_MERRILL} report: \"Grapes\""
    # Harvard
    assert harvard_poetry_cfg.complete_description == 'Harvard poetry stuff from Lisa New'
    # iMessage
    assert CONFIGS_BY_ID['033434'].complete_description == 'iMessage from Brad Edwards (???) screenshot(s)'
    # Junk
    assert junk_doc_cfg.complete_description == ''
    junk_doc_cfg.note = 'junk mail'
    assert junk_doc_cfg.complete_description == 'junk mail'
    # Legal
    assert legal_cfg.complete_description == f"clinton v. trump: case law"
    # Letters
    assert CONFIGS_BY_ID['025704'].complete_description == 'letter from Ken Starr to Judge Mark Filip requesting lenient treatment for Epstein'
    assert CONFIGS_BY_ID['028965'].complete_description == 'letter from Martin Weinberg to Good Morning America threatening libel lawsuit against ABC'
    # Skype
    assert skype_cfg.complete_description == 'Skype log'
    # Skype with author
    assert skype_author.complete_description == f"{SKYPE_LOG} of conversation with linkspirit"
    skype_author.note = 'something'
    assert skype_author.complete_description == f"{SKYPE_LOG} of conversation with linkspirit something"
    # Skype with recipients
    assert skype_recipients.complete_description == f"{SKYPE_LOG} of conversation with LBJ, JFK"
    skype_recipients.author = 'FDR'
    assert skype_recipients.complete_description == f"{SKYPE_LOG} of conversation with FDR, LBJ, JFK"
    # Tweet
    assert tweet_cfg.is_interesting is None
    assert tweet_cfg.complete_description == 'Tweet by Klippenstein'
    tweet_cfg.note = 'libelous'
    assert tweet_cfg.complete_description == 'Tweet by Klippenstein libelous'
    # whatsapp
    assert whatsapp_cfg.complete_description == 'WhatsApp log of conversation with Maria Prusakova about Crypto PR Lab'


@pytest.mark.parametrize(
    "id,category,description",
    [
        pytest.param('026731', Uninteresting.ACADEMIA, 'speech at first inaugural Cornell Carl Sagan Lecture by Lord Martin Rees'),
        pytest.param('010912', Uninteresting.BOOK, 'book titled "Free Growth and Other Surprises" (draft) by Gordon Getty'),
        pytest.param('018438', Uninteresting.BOOK, 'book titled "The S&M Feminist" by Clarisse Thorn'),
        pytest.param('EFTA00006100', Neutral.MISC, ''),
    ]
)
def test_descriptions(get_other_file, id, category, description):
    file = get_other_file(id)
    assert file.config.category == category
    assert file.config.complete_description == description


def test_epstein_will():
    assert CONFIGS_BY_ID['EFTA00089546'].note == f"Epstein last will and testament codicil naming {HENRY_JARECKI}, James Cayne, Paul Hoffman as executors"
    assert CONFIGS_BY_ID['EFTA00016884'].note == f"Epstein last will and testament naming Darren Indyke, David Mitchell, Jes Staley, Larry Summers as executors"


def test_highlight_quote():
    quote_cfg = EmailCfg(id=ID, highlight_quote='somebody to\nscrub > again')
    assert quote_cfg.complete_description == f'{QUOTE_PREFIX}: "somebody to scrub again"'


def test_is_empty(academia_cfg, dummy_cfg, empty_doj_cfg, empty_house_cfg):
    assert not academia_cfg.is_empty
    assert empty_doj_cfg.is_empty
    assert empty_house_cfg.is_empty
    assert dummy_cfg.is_empty


def test_is_of_interest(
    academia_cfg,
    blockchain_cap_cfg,
    empty_doj_cfg,
    empty_house_cfg,
    finance_report,
    fwded_article,
    harvard_poetry_cfg,
    interesting_doc,
    junk_doc_cfg,
    junk_email_cfg,
    legal_cfg,
    skype_cfg,
    uninteresting_description,
    UN_cfg,
    very_interesting_cfg
):
    assert academia_cfg.is_of_interest is False
    assert blockchain_cap_cfg.is_of_interest is True
    assert blockchain_cap_cfg.is_very_interesting is False
    assert empty_doj_cfg.is_of_interest is None
    assert empty_house_cfg.is_of_interest is None
    assert finance_report.is_of_interest is False
    assert fwded_article.is_of_interest is False
    assert harvard_poetry_cfg.is_of_interest is False
    assert interesting_doc.is_of_interest is True
    assert junk_doc_cfg.is_of_interest is False
    assert junk_email_cfg.is_of_interest is False
    assert legal_cfg.is_of_interest is None
    assert skype_cfg.is_of_interest is None
    assert UN_cfg.is_of_interest is True
    assert uninteresting_description.is_of_interest is False
    assert very_interesting_cfg.is_of_interest is True


def test_is_very_interesting(very_interesting_cfg):
    assert very_interesting_cfg.is_very_interesting is True


def test_truthy_props(legal_cfg, dummy_cfg, fwded_article):
    dummy_props = dummy_cfg.truthy_props
    del dummy_props['category_txt']
    assert dummy_props == {'id': dummy_cfg.id, **BASE_TRUTHY_PROPS}

    assert fwded_article.truthy_props == {
        'id': fwded_article.id,
        'author': 'BofA / Merrill Lynch',
        # 'category_txt': Text('journalism'),
        'is_of_interest': False,
        'is_fwded_article': True,
        'is_valid_for_name_scan': False,
    }

    assert legal_cfg.truthy_props == {
        'id': legal_cfg.id,
        'author': 'clinton v. trump',
        'category_txt': Text('legal', 'purple'),
        'complete_description': 'clinton v. trump: case law',
        'is_valid_for_name_scan': True,
        'note': 'case law',
    }


def _oversight_cfg(category: str = '', **kwargs) -> DocCfg:
    return _doc_cfg('123456', category=category, **kwargs)


def _doj_cfg(category: str = '', **kwargs) -> DocCfg:
    return _doc_cfg('EFTA02614678', category=category, **kwargs)


def _doc_cfg(id: str, category: str = '', author: Name = None, **kwargs) -> DocCfg:
    return DocCfg(id=id, category=category, author=author, **kwargs)
