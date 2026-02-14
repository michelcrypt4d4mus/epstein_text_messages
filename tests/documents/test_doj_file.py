

def test_crypto_doc_with_author(epstein_files):
    doc = epstein_files.get_id('EFTA01082451')
    assert doc.category == 'crypto'
    assert doc.info_txt is None
    assert doc.info[0].plain.strip() == 'Blockchain Capital / Coinbase nondisclosure agreement possibly regarding Epstein investment'


def test_valar_cfg_creation(epstein_files):
    doc = epstein_files.get_id('EFTA00609489', rebuild=True)
    assert doc.info[0].plain.strip() == 'Valar Ventures is a Peter Thiel fintech fund'
