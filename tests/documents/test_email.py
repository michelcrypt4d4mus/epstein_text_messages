from epstein_files.documents.email import JUNK_EMAILERS


def test_junk_emailers():
    assert len(JUNK_EMAILERS) == 5
