#!/usr/bin/env python
from scripts.use_pickled import epstein_files
from epstein_files.documents.json_file import JsonFile
from epstein_files.util.rich import console


for json_file in [f for f in epstein_files.other_files if isinstance(f, JsonFile)]:
    console.print(json_file.description_panel())
    console.print_json(json_file.formatted_json())
