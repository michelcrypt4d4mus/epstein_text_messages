#!/usr/bin/env python
import re
from pathlib import Path
from subprocess import run
from sys import argv

from dotenv import load_dotenv
load_dotenv()
from rich.console import Console

from documents.document import Document
from documents.email import Email, REPLY_LINE_PATTERN, REPLY_REGEX, REPLY_TEXT_REGEX, SENT_FROM_REGEX, REDACTED_REPLY_REGEX
from documents.epstein_files import EpsteinFiles
from util.env import is_debug
from util.file_helper import DOCS_DIR


console = Console(color_system='256')
console.print(f"argv: {argv}")
epstein_files = EpsteinFiles()

for line in epstein_files.lines_matching('krauss'):
    console.print(line)
