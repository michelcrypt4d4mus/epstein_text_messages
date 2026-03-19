from epstein_files.documents.document import Document


def test_grand_jury(get_doj_file):
    doc: Document = get_doj_file('EFTA00008863').reload()
    assert doc._config.complete_description == 'grand jury proceedings in U.S. v. Ghislaine Maxwell'
