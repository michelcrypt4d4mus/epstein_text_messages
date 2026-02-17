from datetime import datetime

import pytest

from epstein_files.documents.document import Document
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.epstein_files import count_by_month
from epstein_files.output.rich import console
from epstein_files.util.constant.names import *
from epstein_files.util.constants import CONFIGS_BY_ID
from epstein_files.util.helpers.data_helpers import dict_sets_to_lists

from .fixtures.emails.email_author_counts import EMAIL_AUTHOR_COUNTS
from .fixtures.emails.email_recipient_counts import EMAIL_RECIPIENT_COUNTS
from .fixtures.emails.signatures import AUTHORS_TO_DEVICE_SIGNATURES, DEVICE_SIGNATURE_TO_AUTHORS, SIGNATURE_SUBSTITUTION_COUNTS
from .fixtures.emails.unknown_recipient_file_ids import UNKNOWN_RECIPIENT_FILE_IDS
from .fixtures.file_counts_by_month import EXPECTED_MONTHLY_COUNTS
from .fixtures.messenger_logs.author_counts import MESSENGER_LOG_AUTHOR_COUNTS
from .fixtures.other_files.interesting_file_ids import INTERESTING_FILE_IDS


def test_all_configured_file_ids_exist(epstein_files):
    all_ids = [doc.file_id for doc in epstein_files.all_documents]
    missing_ids = [id for id in CONFIGS_BY_ID.keys() if id not in all_ids]
    assert len(missing_ids) == 0, f"Missing {len(missing_ids)} files that are configured: {missing_ids}"


def test_document_monthly_counts(epstein_files):
    new_counts = count_by_month(epstein_files.all_documents)

    for month, num_docs in new_counts.items():
        assert month in EXPECTED_MONTHLY_COUNTS
        assert num_docs >= EXPECTED_MONTHLY_COUNTS[month], f"Expected {EXPECTED_MONTHLY_COUNTS[month]} for {month}, found {num_docs}"

    num_files_paths = len(epstein_files.file_paths)
    num_document_objs = sum(new_counts.values())
    assert num_document_objs == num_files_paths - 1256  # There's 1256 empty files


def test_imessage_text_counts(epstein_files):
    assert len(epstein_files.imessage_logs) == 77
    assert MessengerLog.count_authors(epstein_files.imessage_logs) == MESSENGER_LOG_AUTHOR_COUNTS


def test_interesting_other_files(epstein_files):
    interesting_other_file_ids = sorted([f.file_id for f in epstein_files.interesting_other_files])
    assert interesting_other_file_ids == sorted(INTERESTING_FILE_IDS)


def test_no_files_after_2025(epstein_files):
    bad_docs = [d for d in epstein_files.all_documents if d.timestamp and d.timestamp > datetime(2025, 1, 1)]

    for doc in bad_docs:
        console.print(doc)

    assert len(bad_docs) == 0


def test_other_files_author_count(epstein_files):
    known_author_count = Document.known_author_count(epstein_files.other_files)
    assert known_author_count == 438
    assert len(epstein_files.json_files) == 19


def test_other_files_categories(epstein_files):
    assert len([f for f in epstein_files.other_files if not f.category]) == 2298


################################################
#################### EMAILS ####################
################################################

# @pytest.mark.skip(reason='temporary')
def test_email_author_counts(epstein_files):
    author_counts = epstein_files.email_author_counts()
    assert author_counts.pop(JEFFREY_EPSTEIN) > 790
    assert author_counts.pop(LESLEY_GROFF) > 100
    assert author_counts.pop(RICHARD_KAHN) > 50
    assert author_counts == EMAIL_AUTHOR_COUNTS


# @pytest.mark.skip(reason='temporary')
def test_email_recipient_counts(epstein_files):
    recipient_counts = epstein_files.email_recipient_counts()
    assert recipient_counts.pop(JEFFREY_EPSTEIN) > 1800
    assert recipient_counts.pop(LESLEY_GROFF) > 40
    assert recipient_counts.pop(RICHARD_KAHN) > 50
    assert recipient_counts == EMAIL_RECIPIENT_COUNTS


def test_interesting_emails(epstein_files):
    interesting_email_count = len([e for e in epstein_files.unique_emails if e.is_interesting])
    uninteresting_emails_count = len([e for e in epstein_files.unique_emails if e.is_interesting is False])
    assert interesting_email_count == 115
    assert uninteresting_emails_count == 139


def test_signature_substitutions(epstein_files):
    substitution_counts = epstein_files.email_signature_substitution_counts()
    assert substitution_counts.pop(JEFFREY_EPSTEIN) > 3900
    assert substitution_counts == SIGNATURE_SUBSTITUTION_COUNTS


def test_signatures(epstein_files):
    assert dict_sets_to_lists(epstein_files.email_authors_to_device_signatures()) == AUTHORS_TO_DEVICE_SIGNATURES
    assert dict_sets_to_lists(epstein_files.email_device_signatures_to_authors()) == DEVICE_SIGNATURE_TO_AUTHORS


def test_unknown_recipient_file_ids(epstein_files):
    unknown_recipient_ids = epstein_files.unknown_recipient_ids()
    assert unknown_recipient_ids == sorted(UNKNOWN_RECIPIENT_FILE_IDS)
