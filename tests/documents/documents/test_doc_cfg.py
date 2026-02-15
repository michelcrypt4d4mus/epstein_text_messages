from epstein_files.documents.documents.doc_cfg import DocCfg, EmailCfg
from epstein_files.util.constant.strings import *


def test_legal():
    legal_cfg = _doc_cfg(LEGAL, 'clinton v. trump', 'case law')
    assert legal_cfg.complete_description == f"clinton v. trump: case law"


def test_junk():
    junk_cfg = _doc_cfg(JUNK)
    assert junk_cfg.complete_description == ''
    junk_cfg.description = 'junk mail'
    assert junk_cfg.complete_description == 'junk mail'


def test_skype_log():
    cfg = _doc_cfg(SKYPE_LOG)
    assert cfg.complete_description == SKYPE_LOG.lower()
    cfg.author = 'linkspirit'
    assert cfg.complete_description == f"{SKYPE_LOG.lower()} of conversation with linkspirit"
    cfg.description = 'something'
    assert cfg.complete_description == f"{SKYPE_LOG.lower()} of conversation with linkspirit something"


def _doc_cfg(category: str = '', author: str = '', description: str = '') -> DocCfg:
    return DocCfg(id='123456', category=category, author=author, description=description)
