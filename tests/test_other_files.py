from epstein_files.documents.document import Document


def test_other_files_author_count(epstein_files):
    assert Document.known_author_count(epstein_files.other_files) == 353
    assert len(epstein_files.json_files) == 19
