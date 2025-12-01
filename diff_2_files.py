#!/usr/bin/env python
from pathlib import Path
from subprocess import run

from dotenv import load_dotenv
load_dotenv()

from documents.document import Document
from util.env import args
from util.file_helper import DOCS_DIR


if len(args.positional_args) != 2:
    raise RuntimeError(f"Need 2 args, got {len(args.positional_args)}")
elif args.positional_args[0] == args.positional_args[1]:
    raise RuntimeError(f"Filenames are the same!")

files = args.positional_args
tmpfiles = [Path(f"tmp_{f}") for f in files]
docs = [Document(DOCS_DIR.joinpath(f)) for f in files]

for i, doc in enumerate(docs):
    doc.write_clean_text(tmpfiles[i])

cmd = f"diff {tmpfiles[0]} {tmpfiles[1]}"
print(f"Running '{cmd}'...")
results = run(cmd, shell=True, capture_output=True, text=True).stdout
print(f"\nDiff results:\n{results}\n")

for f in tmpfiles:
    print(f"\nDeleting '{f}'...")
    f.unlink()
