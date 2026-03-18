#!/usr/bin/env python
# Copy any emails extracted from legal filings into the repo.
import csv
from datetime import datetime, timezone, timedelta
from copy import copy
from pathlib import Path

from dateutil.parser import parse

from scripts.use_pickled import console, epstein_files
from epstein_files.documents.document import Document
from epstein_files.documents.email import Email
from epstein_files.util.helpers.data_helpers import days_between_abs
from epstein_files.util.helpers.file_helper import file_size_str
from epstein_files.util.env import args
from epstein_files.util.logging import logger
from epstein_files.util.timer import Timer

from ..conftest import FILE_INFO_CSV_PATH

EMPTY_STRING_PROPS = [
    'category',
]

ROOT_PROPS = ['file_id'] + EMPTY_STRING_PROPS + [
    'author',
    'is_interesting',
]

EMAIL_PROPS = [
    'recipients_str',
    'sent_from_device',
]

CFG_PROPS = [
    'complete_description'
]

COLS = ROOT_PROPS + ['timestamp'] + EMAIL_PROPS + CFG_PROPS


def load_files_csv() -> dict[str, dict[str, bool | datetime | str | None]]:
    """Read the CSV of file information and coerce appropriate fields for comparison."""
    rows_by_id = {}

    with open(FILE_INFO_CSV_PATH, mode ='r') as file:
        for row in csv.DictReader(file):
            for k in row.keys():
                val = row[k]

                if val == '' and not (k.endswith('_str') or k in EMPTY_STRING_PROPS):
                    row[k] = None
                elif val in ['True', 'False']:
                    row[k] = True if val == 'True' else False
                elif k == 'timestamp':
                    row[k] = parse(row[k])

            rows_by_id[row.pop('file_id')] = row

    return rows_by_id


def is_timestamp_different(dt1: datetime | None, dt2: datetime | None) -> bool | str:
    """lack of tz means doc.timestamp moves around :(. returns `str` if just a warning."""
    timestamps = [dt1, dt2]

    if all(d is None for d in timestamps):
        return False
    elif all(isinstance(t, datetime) for t in timestamps):
        if dt1 == dt2:
            return False
        elif (days := days_between_abs(dt1, dt1)) <= 3:
            return f"timestamps differ by acceptable range of {days - 1} days ({dt1} vs {dt2}), using old timestamp"
        else:
            return True
    else:
        return True


def write_files_csv():
    rows_by_id = load_files_csv()
    timer = Timer()
    rows = []

    for doc in Document.sort_by_id(epstein_files.unique_documents):
        row = {k: getattr(doc, k) for k in ROOT_PROPS}
        old_timestamp = (rows_by_id.get(doc.file_id) or {}).get('timestamp')
        has_timestamp_diff = is_timestamp_different(doc.timestamp, old_timestamp)

        if isinstance(has_timestamp_diff, str):
            doc._warn(has_timestamp_diff)
            row['timestamp'] = old_timestamp
        else:
            row['timestamp'] = doc.timestamp

        row.update({k: (getattr(doc, k) if isinstance(doc, Email) else None) for k in EMAIL_PROPS})
        row.update({k: (getattr(doc.config, k) if doc.config else None) for k in CFG_PROPS})
        rows.append(row)

    with open(FILE_INFO_CSV_PATH, 'w') as f:
        writer = csv.DictWriter(f, COLS)
        writer.writeheader()
        writer.writerows(rows)

    if args.debug:
        console.print('\n\n' + FILE_INFO_CSV_PATH.read_text())

    timer.print_at_checkpoint(f"Wrote {file_size_str(FILE_INFO_CSV_PATH)} to '{FILE_INFO_CSV_PATH}'.")
