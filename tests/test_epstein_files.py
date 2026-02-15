from datetime import datetime

from epstein_files.documents.document import Document
from epstein_files.documents.other_file import OtherFile

from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.epstein_files import count_by_month
from epstein_files.output.rich import console
from epstein_files.util.constant.names import *
from epstein_files.util.constants import CONFIGS_BY_ID

from .fixtures.file_counts_by_month import EXPECTED_MONTHLY_COUNTS
from .fixtures.messenger_logs.author_counts import MESSENGER_LOG_AUTHOR_COUNTS
from .fixtures.other_files.interesting_file_ids import INTERESTING_FILE_IDS


def test_all_configured_file_ids_exist(epstein_files):
    all_ids = [doc.file_id for doc in epstein_files.all_documents]
    missing_ids = [id for id in CONFIGS_BY_ID.keys() if id not in all_ids]
    assert len(missing_ids) == 0, f"Missing {len(missing_ids)} files that are configured: {missing_ids}"


def test_document_monthly_counts(epstein_files):
    counts = count_by_month(epstein_files.all_documents)
    assert counts == EXPECTED_MONTHLY_COUNTS
    len_all_files = len(epstein_files.all_files)
    assert sum(counts.values()) == len_all_files - 1256  # There's 1246 empty files # TODO: this is the wrong number?


def test_imessage_text_counts(epstein_files):
    assert len(epstein_files.imessage_logs) == 77
    assert MessengerLog.count_authors(epstein_files.imessage_logs) == MESSENGER_LOG_AUTHOR_COUNTS


def test_interesting_file_count(epstein_files):
    interesting_other_file_ids = sorted([f.file_id for f in epstein_files.interesting_other_files])
    assert interesting_other_file_ids == sorted(INTERESTING_FILE_IDS)


def test_no_files_after_2025(epstein_files):
    bad_docs = [d for d in epstein_files.all_documents if d.timestamp and d.timestamp > datetime(2025, 1, 1)]

    for doc in bad_docs:
        console.print(doc)

    assert len(bad_docs) == 0


def test_other_files_author_count(epstein_files):
    known_author_count = Document.known_author_count(epstein_files.other_files)
    assert known_author_count == 418
    assert len(epstein_files.json_files) == 19


def test_other_files_categories(epstein_files):
    assert len([f for f in epstein_files.other_files if not f.category]) == 2425
