#!/usr/bin/env python
# Pretty print all the JSON files in the collection.
from scripts.use_pickled import console, epstein_files
from epstein_files.documents.json_file import JsonFile


for json_file in [f for f in epstein_files.other_files if isinstance(f, JsonFile)]:
    console.print(json_file.description_panel())
    console.print_json(json_file.formatted_json())
