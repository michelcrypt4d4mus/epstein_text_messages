#!/usr/bin/env python
# Copy any emails extracted from legal filings into the repo.
import csv
import gzip
from datetime import datetime
from pathlib import Path

from dateutil.parser import parse

from scripts.use_pickled import console, epstein_files
from epstein_files.documents.document import Document
from epstein_files.documents.email import Email
from epstein_files.util.helpers.file_helper import file_size_str
from epstein_files.util.logging import logger
from epstein_files.util.timer import Timer

from ..conftest import FILE_INFO_CSV_PATH

ROOT_PROPS = ['file_id', 'is_interesting', 'author', 'timestamp']
EMAIL_PROPS = ['recipients_str', 'sent_from_device']
CFG_PROPS = ['complete_description']
COLS = ROOT_PROPS + EMAIL_PROPS + CFG_PROPS


def load_files_csv() -> dict[str, dict[str, bool | datetime | str | None]]:
    rows_by_id = {}

    with open(FILE_INFO_CSV_PATH, mode ='r') as file:
        for row in csv.DictReader(file):
            for k in row.keys():
                if k.startswith('is_'):
                    if row[k] == 'True':
                        row[k] = True
                    elif row[k] == 'False':
                        row[k] = False
                    elif row[k] == '':
                        row[k] = None
                    else:
                        raise RuntimeError(f"Bad row {row}")
                elif row[k] == '' and not k.endswith('str'):
                    row[k] = None
                elif k == 'timestamp':
                    row[k] = parse(row[k])

            rows_by_id[row.pop('file_id')] = row

    return rows_by_id


def write_files_csv():
    timer = Timer()
    rows = []

    for doc in Document.sort_by_id(epstein_files.unique_documents):
        row = {k: getattr(doc, k) for k in ROOT_PROPS}
        row.update({k: (getattr(doc, k) if isinstance(doc, Email) else None) for k in EMAIL_PROPS})
        row.update({k: (getattr(doc.config, k) if doc.config else None) for k in CFG_PROPS})
        rows.append(row)

    with open(FILE_INFO_CSV_PATH, 'wt') as f:
        timer.print_at_checkpoint(f'Built {len(rows)} rows')
        writer = csv.DictWriter(f, COLS)
        writer.writeheader()
        writer.writerows(rows)

    logger.warning(f"Wrote {file_size_str(FILE_INFO_CSV_PATH)}to '{FILE_INFO_CSV_PATH}'.")
