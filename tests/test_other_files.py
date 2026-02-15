from epstein_files.documents.document import Document
from epstein_files.documents.other_file import OtherFile

import pytest

from .fixtures.other_files.interesting_file_ids import INTERESTING_FILE_IDS


def test_interesting_file_count(epstein_files):
    interesting_file_ids = sorted([f.file_id for f in epstein_files.interesting_other_files])
    assert len(interesting_file_ids) == len(INTERESTING_FILE_IDS)
    assert interesting_file_ids == sorted(INTERESTING_FILE_IDS)


def test_other_files_author_count(epstein_files):
    known_author_count = Document.known_author_count(epstein_files.other_files)
    assert known_author_count == 418
    assert len(epstein_files.json_files) == 19


def test_other_files_categories(epstein_files):
    assert len([f for f in epstein_files.other_files if not f.category]) == 2425
