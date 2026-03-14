#!/usr/bin/env python
from pathlib import Path

#from epstein_files.util.helpers.file_helper import DRO
from scripts.use_pickled import console, epstein_files
from epstein_files.util.helpers.file_helper import file_size_str

from tests.conftest import FILE_TEXT_DUMP_DIR


for doc in epstein_files.documents:
    output_file = FILE_TEXT_DUMP_DIR.joinpath(doc.file_id)
    output_file.write_text(doc.text)
    doc._warn(f"Wrote {file_size_str(output_file)}...")
