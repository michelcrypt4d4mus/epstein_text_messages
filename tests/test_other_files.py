from epstein_files.documents.document import Document


def test_other_files_author_count(epstein_files):
    known_author_count = Document.known_author_count(epstein_files.other_files)
    assert known_author_count == 370
    assert len(epstein_files.json_files) == 19


def test_other_files_categories(epstein_files):
    assert len([f for f in epstein_files.other_files if f.category() is None]) == 0


def test_interesting_file_count(epstein_files):
    assert len([f.file_id for f in epstein_files.other_files if f.is_interesting()]) == 160
