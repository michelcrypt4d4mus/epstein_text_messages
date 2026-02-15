from datetime import datetime

from epstein_files.epstein_files import count_by_month
from epstein_files.output.rich import console
from epstein_files.util.constants import CONFIGS_BY_ID

from .fixtures.file_counts_by_month import EXPECTED_MONTHLY_COUNTS


def test_all_configs_exist(epstein_files):
    all_ids = [doc.file_id for doc in epstein_files.all_documents]
    missing_ids = [id for id in CONFIGS_BY_ID.keys() if id not in all_ids]
    assert len(missing_ids) == 0, f"Missing {len(missing_ids)} files that are configured: {missing_ids}"


def test_document_monthly_counts(epstein_files):
    counts = count_by_month(epstein_files.all_documents)
    assert counts == EXPECTED_MONTHLY_COUNTS
    len_all_files = len(epstein_files.all_files)
    assert sum(counts.values()) == len_all_files - 1256  # There's 1246 empty files # TODO: this is the wrong number?


def test_no_files_after_2025(epstein_files):
    bad_docs = [d for d in epstein_files.all_documents if d.timestamp and d.timestamp > datetime(2025, 1, 1)]

    for doc in bad_docs:
        console.print(doc)

    assert len(bad_docs) == 0
