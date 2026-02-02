from epstein_files.util.constant.strings import *
from epstein_files.util.doc_cfg import DocCfg, EmailCfg


def test_complete_description():
    cfg = _doc_cfg(SKYPE_LOG)
    assert cfg.complete_description == SKYPE_LOG
    cfg.author = 'linkspirit'
    assert cfg.complete_description == f"{SKYPE_LOG} of conversation with linkspirit"
    cfg.description = 'something'
    assert cfg.complete_description == f"{SKYPE_LOG} of conversation with linkspirit something"

    legal_cfg = _doc_cfg(LEGAL, 'clinton v. trump', 'case law')
    assert legal_cfg.complete_description == f"clinton v. trump: case law"


def _doc_cfg(category: str | None = None, author: str | None = None, description: str | None = None) -> DocCfg:
    return DocCfg(id='123456', category=category, author=author, description=description)
