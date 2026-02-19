#!/usr/bin/env python
# Copy any emails extracted from legal filings into the repo.
import csv
import shutil
from pathlib import Path

from scripts.use_pickled import console, epstein_files
from epstein_files.documents.document import Document
from epstein_files.util.helpers.file_helper import file_size_str

FIXTURES_DIR = Path(__file__).parent.parent.joinpath('tests', 'fixtures', 'generated')
FILE_INFO_CSV_PATH = FIXTURES_DIR.joinpath('interesting_other_files.csv')
COLS = ['file_id', 'is_interesting', 'author', 'timestamp', 'complete_description']


def write_files_csv():
    with open(FILE_INFO_CSV_PATH, 'wt') as f:
        writer = csv.DictWriter(f, COLS)

        for doc in Document.sort_by_id(epstein_files.unique_documents):
            writer.writerow({k: v for k, v in doc._debug_dict(with_prefixes=False).items() if k in COLS})


write_files_csv()
console.print(f"Wrote {len(epstein_files.documents)} to '{FILE_INFO_CSV_PATH}' ({file_size_str(FILE_INFO_CSV_PATH)})")
