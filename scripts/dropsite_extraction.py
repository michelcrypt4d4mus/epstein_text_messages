#!/usr/bin/env python
#from epstein_files.util.helpers.file_helper import DRO
from epstein_files.util.env import DROPSITE_EMLS_DIR
from epstein_files.documents.emails.eml import Eml
from epstein_files.output.rich import console


emls = []

for eml_path in DROPSITE_EMLS_DIR.glob('*.eml'):
    print(eml_path)
    emls.append(Eml(eml_path))
    console.print(emls[-1])
