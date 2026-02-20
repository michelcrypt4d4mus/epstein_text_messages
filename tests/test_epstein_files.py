
from datetime import datetime

import pytest

from epstein_files.documents.document import Document
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.output.rich import console, print_subtitle_panel
from epstein_files.util.constant.names import *
from epstein_files.util.constants import CONFIGS_BY_ID
from epstein_files.util.helpers.data_helpers import dict_sets_to_lists

from .conftest import assert_higher_counts
from .fixtures.emails.signatures import AUTHORS_TO_DEVICE_SIGNATURES, DEVICE_SIGNATURE_TO_AUTHORS, SIGNATURE_SUBSTITUTION_COUNTS
from .fixtures.messenger_logs.author_counts import MESSENGER_LOG_AUTHOR_COUNTS
from .fixtures.fixture_csvs import EMAIL_PROPS, load_files_csv


def test_against_csv(epstein_files):
    """CSV data can be updated by running './scripts/update_fixture_csv.py'."""
    csv_docs = load_files_csv()
    bad_docs = []

    for doc in epstein_files.unique_documents:
        if (csv_row := csv_docs.get(doc.file_id)):
            for k, csv_val in csv_row.items():
                if k == 'complete_description' or (k in EMAIL_PROPS and not isinstance(doc, Email)):
                    continue
                elif (doc_prop := getattr(doc, k)) != csv_val:
                    doc.warn(f"mismatched values for {k}! doc has {doc_prop}, csv has {csv_val}")
                    bad_docs.append(doc)
        else:
            print_subtitle_panel(f"CSV is missing {doc.file_id}", center=False)
            console.print(doc)
            bad_docs.append(doc)
            continue

    num_bad_docs = len(bad_docs)
    assert num_bad_docs == 0


def test_all_configured_file_ids_exist(epstein_files):
    all_ids = [doc.file_id for doc in epstein_files.documents]
    missing_ids = [id for id in CONFIGS_BY_ID.keys() if id not in all_ids]
    assert len(missing_ids) == 0, f"Missing {len(missing_ids)} files that are configured: {missing_ids}"


def test_imessage_text_counts(epstein_files):
    assert len(epstein_files.imessage_logs) == 77
    assert MessengerLog.count_authors(epstein_files.imessage_logs) == MESSENGER_LOG_AUTHOR_COUNTS


def test_no_files_after_2025(epstein_files):
    bad_docs = [d for d in epstein_files.documents if d.timestamp and d.timestamp > datetime(2025, 1, 1)]

    for doc in bad_docs:
        console.print(doc)

    assert len(bad_docs) == 0


def test_other_files_categories(epstein_files):
    assert len([f for f in epstein_files.other_files if not f.category]) == 2235


def test_signature_substitutions(epstein_files):
    substitution_counts = epstein_files.email_signature_substitution_counts()
    assert_higher_counts(substitution_counts, SIGNATURE_SUBSTITUTION_COUNTS)


def test_signatures(epstein_files):
    authors_to_devices = epstein_files.email_authors_to_device_signatures()
    devices_to_authors = epstein_files.email_device_signatures_to_authors()

    for name in [JEFFREY_EPSTEIN, LINDA_STONE, STEVEN_SINOFSKY]:
        assert authors_to_devices[name] == set(AUTHORS_TO_DEVICE_SIGNATURES[name])

    for signature in ["Sent from my BlackBerry 10 smartphone."]:
        assert devices_to_authors[signature] == set(DEVICE_SIGNATURE_TO_AUTHORS[signature])
