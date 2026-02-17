import pytest

from epstein_files.documents.doj_file import DojFile


def test_crypto_doc_with_author(blockchain_capital_coinbase_nda):
    assert blockchain_capital_coinbase_nda.category == 'crypto'
    assert blockchain_capital_coinbase_nda.subheader is None
    assert blockchain_capital_coinbase_nda.info[0].plain.strip() == \
        'Blockchain Capital / Coinbase nondisclosure agreement possibly regarding Epstein investment'


def test_valar_cfg_creation(valar_ventures_doc):
    assert valar_ventures_doc.config is not None
    assert valar_ventures_doc.info[0].plain.strip() == 'Valar Ventures is a fintech focused Peter Thiel fund Epstein was invested in'
