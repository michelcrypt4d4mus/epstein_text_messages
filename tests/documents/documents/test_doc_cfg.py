import pytest
from copy import deepcopy

from epstein_files.documents.documents.doc_cfg import DocCfg, EmailCfg
from epstein_files.util.constant.strings import *

RANDOM_ID = '123456'


@pytest.fixture
def junk_doc_cfg() -> DocCfg:
    return DocCfg(id=RANDOM_ID, category=JUNK)


@pytest.fixture
def junk_email_cfg() -> EmailCfg:
    return EmailCfg(id=RANDOM_ID, category=JUNK, author='who knows')


@pytest.fixture
def legal_cfg() -> DocCfg:
    return _doc_cfg(LEGAL, 'clinton v. trump', 'case law')


@pytest.fixture
def skype_cfg() -> DocCfg:
    return _doc_cfg(SKYPE_LOG)


@pytest.fixture
def skype_author() -> DocCfg:
    return _doc_cfg(SKYPE_LOG, author='linkspirit')


def test_category_txt(junk_doc_cfg, legal_cfg, skype_cfg, skype_author):
    assert junk_doc_cfg.category_txt.plain == JUNK
    assert skype_cfg.category_txt.plain == SKYPE_LOG
    import pdb;pdb.set_trace

def test_complete_description(junk_doc_cfg, legal_cfg, skype_cfg, skype_author):
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


def test_is_of_interest(junk_doc_cfg, junk_email_cfg, legal_cfg, skype_cfg):
    assert junk_doc_cfg.is_of_interest is False
    assert junk_email_cfg.is_of_interest is False
    assert legal_cfg.is_of_interest is None
    assert skype_cfg.is_of_interest is None


def _doc_cfg(category: str = '', author: str = '', description: str = '') -> DocCfg:
    return DocCfg(id='123456', category=category, author=author, description=description)
