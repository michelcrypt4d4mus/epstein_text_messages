#!/usr/bin/env python
# Copy any emails extracted from legal filings into the repo.
import csv
import shutil
from pathlib import Path

from scripts.use_pickled import console, epstein_files
from epstein_files.documents.document import Document
from epstein_files.util.helpers.file_helper import file_size_str
from epstein_files.util.logging import logger
from epstein_files.util.timer import Timer

from tests.fixtures.fixture_csvs import load_files_csv, write_files_csv


write_files_csv()
load_files_csv()
