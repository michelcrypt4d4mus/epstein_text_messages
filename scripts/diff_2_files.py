#!/usr/bin/env python
from dotenv import load_dotenv
load_dotenv()

from epstein_files.documents.document import Document
from epstein_files.util.env import args


Document.diff_files(args.positional_args)
