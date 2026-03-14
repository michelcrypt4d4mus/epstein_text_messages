#!/usr/bin/env python
# Update the CSV fixtures with the Document props pytest compares against.
from epstein_files.util.logging import logger

from scripts.use_pickled import epstein_files
from tests.conftest import FILE_TEXT_DUMP_DIR
from tests.fixtures.fixture_csvs import load_files_csv, write_files_csv


def update_text_dump() -> None:
    for doc in epstein_files.documents:
        output_file = FILE_TEXT_DUMP_DIR.joinpath(doc.file_id)

        if output_file.exists():
            if (old_contents := output_file.read_text()) == doc.text:
                doc.log(f"text matches '{output_file}', skipping...")
                continue

            num_diff_chars = doc.length - len(old_contents)
            doc._warn(f"updating existing file at '{output_file}' with {num_diff_chars} new chars...")
        else:
            doc._warn(f"file doesn't exist, writing {len(doc.text)} chars to '{output_file}'...")

        output_file.write_text(doc.text)


write_files_csv()
update_text_dump()
