#!/usr/bin/env python
# Print email ID + timestamp
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

from scripts.use_pickled import *
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.rich import console, print_json


epstein_files = EpsteinFiles.get_files()
max_file_sizes = defaultdict(int)

for doc in sorted(epstein_files.all_documents(), key=lambda e: e.file_id):
    console.print(doc.summary())
    max_file_sizes[doc.class_name()] = max(max_file_sizes[doc.class_name()], doc.file_size())

console.line(2)
print_json(f"Largest files found", max_file_sizes)
