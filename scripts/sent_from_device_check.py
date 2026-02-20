#!/usr/bin/env python
from epstein_files.documents.email import Email
from epstein_files.util.logging import logger
from tests.fixtures.fixture_csvs import load_files_csv
from scripts.use_pickled import console, epstein_files


docs_by_id = epstein_files._docs_by_id()
doc_ids_to_fix = []

for id, row in load_files_csv().items():
    doc = docs_by_id[id]

    if not isinstance(doc, Email):
        continue
    elif not (csv_device := row['sent_from_device']):
        continue

    doc_device = doc._sent_from_device()

    if doc_device != csv_device:
        doc_ids_to_fix.append(doc.file_id)
        doc.warn(f"Extracted device doesn't match CSV!\n  doc: \"{doc_device}\"\n  csv: \"{csv_device}\"")
    else:
        console.print(f"{id} matches", style='green')

print(f"Need to fix these ids: {' '.join(doc_ids_to_fix)}")
