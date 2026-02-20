#!/usr/bin/env python
# Update the CSV fixtures with the Document props pytest compares against.
from pathlib import Path

from epstein_files.util.logging import logger

from tests.fixtures.fixture_csvs import load_files_csv, write_files_csv


write_files_csv()

# for id, props in load_files_csv().items():
#     if any(v for v in props.items()):
#         print(f'{id}: {props}')
