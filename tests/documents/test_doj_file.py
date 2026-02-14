

def test_crypto_doc_with_author(epstein_files):
    doc = epstein_files.for_ids('EFTA01082451')[0]
    assert doc.category == 'crypto'
    assert doc.info_txt is None
    assert doc.info[0].plain.strip() == 'Blockchain Capital / Coinbase nondisclosure agreement possibly regarding Epstein investment'
