from datetime import datetime
from itertools import chain

import pytest
from rich.panel import Panel

from epstein_files.documents.document import Document
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile
from epstein_files.output.rich import console, print_subtitle_panel
from epstein_files.people.names import *
from epstein_files.util.constants import CONFIGS_BY_ID
from epstein_files.util.helpers.data_helpers import days_between, uniquify
from epstein_files.util.helpers.file_helper import diff_files
from epstein_files.util.helpers.string_helper import prop_str

from .conftest import FILE_TEXT_DUMP_DIR, assert_higher_counts
from .fixtures.emails.signatures import AUTHORS_TO_DEVICE_SIGNATURES, DEVICE_SIGNATURE_TO_AUTHORS, SIGNATURE_SUBSTITUTION_COUNTS
from .fixtures.messenger_logs.author_counts import IMESSAGE_LOG_IDS, MESSENGER_LOG_AUTHOR_COUNTS
from .fixtures.fixture_csvs import CFG_PROPS, EMAIL_PROPS, load_files_csv

COMMON_DEVICE_SIGNATURES = [
    set(["Sent from my iPad"]),
    set(["Sent from my iPhone"]),
    set(["Sent from my iPad", "Sent from my iPhone"]),
]


def test_against_csv(epstein_files):
    """CSV data can be updated by running './scripts/update_file_fixtures.py'."""
    csv_docs = load_files_csv()
    bad_docs = []
    repair_ids = []

    for doc in epstein_files.non_duplicate_docs:
        if (csv_row := csv_docs.get(doc.file_id)):
            for k, csv_val in csv_row.items():
                if k in EMAIL_PROPS and not isinstance(doc, Email):
                    continue
                elif k in CFG_PROPS:
                    doc_val = getattr(doc.config, k) if doc.config else ''
                else:
                    doc_val = getattr(doc, k)

                    if doc_val == csv_val:
                        continue
                    elif all(isinstance(v, datetime) for v in [csv_val, doc_val]) and \
                            (days := abs(days_between(csv_val, doc_val))) <= 3:
                        doc._warn(f"timestamps differ by {days - 1} days, just a warning ({doc_val} vs {csv_val})")
                        continue

                    bad_docs.append(doc)
                    repair_ids.append(doc.file_id)
                    reloaded_prop = getattr(doc.reload(), k)
                    mismatched_prop_str = f"mismatched '{k}'"
                    values_str = f"doc={prop_str(doc_val)}', csv={prop_str(csv_val)}"

                    if reloaded_prop == csv_val:
                        values_str += f", reloaded='{reloaded_prop}'"
                        doc._warn(f"{mismatched_prop_str} in gzip but reloaded is OK ({values_str})")
                    else:
                        doc._warn(f"{mismatched_prop_str} ({values_str})")
        else:
            print_subtitle_panel(f"CSV is missing {doc.file_id}", center=False)
            console.print(doc)
            bad_docs.append(doc)
            continue

    bad_ids = uniquify([doc.file_id for doc in bad_docs])
    assert len(bad_ids) == 0, f"{len(bad_ids)} docs don't match CSV, {len(repair_ids)} might be reparable: {' '.join(repair_ids)}"


def test_file_contents(epstein_files):
    """Run `scripts/update_file_fixtures.py` to write/update the .txt files that will be tested against."""
    errors = []

    for doc in epstein_files.unique_documents:
        old_contents_path = FILE_TEXT_DUMP_DIR.joinpath(doc.file_id)

        if not old_contents_path.exists():
            errors.append(f"No file found at '{old_contents_path}' to compare against!")
            continue
        elif old_contents_path.read_text() != doc.text:
            errors.append(f"{doc.file_id} text doesn't match '{old_contents_path}'")

            with doc._write_tmp_file() as new_contents_tmp_path:
                diff_files(old_contents_path, new_contents_tmp_path, print_to_console=True)

    assert errors == []


def test_all_configured_file_ids_exist(epstein_files):
    all_ids = [doc.file_id for doc in epstein_files._documents]
    missing_ids = [id for id in CONFIGS_BY_ID.keys() if id not in all_ids]
    assert len(missing_ids) == 0, f"Missing {len(missing_ids)} files that are configured: {missing_ids}"


def test_imessage_text_counts(epstein_files):
    immesage_log_ids = sorted([doc.file_id for doc in epstein_files.imessage_logs])
    assert immesage_log_ids == IMESSAGE_LOG_IDS
    assert MESSENGER_LOG_AUTHOR_COUNTS == MessengerLog.count_authors(epstein_files.imessage_logs)


def test_no_files_after_2025(epstein_files):
    bad_docs = [d for d in epstein_files.documents if d.timestamp and d.timestamp > Document.MAX_TIMESTAMP]

    for doc in bad_docs:
        console.print(doc)

    assert len(bad_docs) == 0


def test_signature_substitutions(epstein_files):
    substitution_counts = epstein_files.email_signature_substitution_counts()
    assert_higher_counts(substitution_counts, SIGNATURE_SUBSTITUTION_COUNTS)


def test_signatures(epstein_files):
    authors_to_devices = epstein_files.email_authors_to_device_signatures()
    devices_to_authors = epstein_files.email_device_signatures_to_authors()
    all_authors = uniquify([k for k in chain(authors_to_devices.keys(), AUTHORS_TO_DEVICE_SIGNATURES.keys())])

    for name in all_authors:
        assert name in authors_to_devices, f"{name} is in AUTHORS_TO_DEVICE_SIGNATURES but not in results!"
        device_signatures = set(authors_to_devices[name])

        if device_signatures not in COMMON_DEVICE_SIGNATURES:
            assert name in AUTHORS_TO_DEVICE_SIGNATURES, f"{name} has {device_signatures} signatures, fixture has none!"
            fixture_signatures = set(AUTHORS_TO_DEVICE_SIGNATURES[name])
            assert device_signatures == fixture_signatures, f"{name} has {device_signatures} signatures, should have {fixture_signatures}"

    for signature in ["Sent from my BlackBerry 10 smartphone."]:
        assert devices_to_authors[signature] == set(DEVICE_SIGNATURE_TO_AUTHORS[signature])


def test_big_files_were_split_up(epstein_files, split_up_big_email):
    all_doc_ids = [doc.file_id for doc in epstein_files.documents]
    assert split_up_big_email.file_id not in all_doc_ids
    assert split_up_big_email._was_split_up is True
    assert split_up_big_email.reload()._was_split_up is False
