#!/usr/bin/env python
from pathlib import Path
from subprocess import run

from dotenv import load_dotenv
load_dotenv()

from epstein_files.documents.document import Document
from epstein_files.util.env import args
from epstein_files.util.file_helper import DOCS_DIR, extract_file_id


if len(args.positional_args) != 2:
    raise RuntimeError(f"Need 2 args, got {len(args.positional_args)}")
elif args.positional_args[0] == args.positional_args[1]:
    raise RuntimeError(f"Filenames are the same!")

Document.diff_files(args.positional_args)
