#!/usr/bin/env python
import re
from pathlib import Path
from subprocess import run

from dotenv import load_dotenv
load_dotenv()
from rich.console import Console
from rich.text import Text

from documents.document import Document
from documents.email import Email, REPLY_LINE_PATTERN, REPLY_REGEX, REPLY_TEXT_REGEX
from util.env import deep_debug, is_debug
from util.file_helper import DOCS_DIR


console = Console(color_system='256')
cmd = f'egrep -i "^(On|In a message dated) .*" {DOCS_DIR}/*.txt'
print(f"egrep command: '{cmd}'")
results = run(cmd, shell=True, capture_output=True, text=True, check=True).stdout

if deep_debug:
    print("\n\ncommand results:\n", results)

lines = [l.strip().removeprefix(str(DOCS_DIR)) for l in results.split('\n') if len(l.strip()) > 0]
print(f"Found {len(lines)} potential reply lines to check...")
matches = 0
failures = 0
FILE_PREFIX_LENGTH = len('HOUSE_OVERSIGHT_032430.txt:')
MIN_LINE_LENGTH = FILE_PREFIX_LENGTH + 14
MAX_LINE_LENGTH = FILE_PREFIX_LENGTH + 170


# Matched 4631 of 6997 potential signatuares, 2366 failures.
for _line in lines:
    if len(_line) < MIN_LINE_LENGTH or _line.endswith('.ichat'):
        console.print(f'  -> Skipping empty, short, or ichat line: "{_line}"', style='dim')
        continue
    elif len(_line) > MAX_LINE_LENGTH:
        console.print(f'  -> Skipping long line: "{_line[0:90]}..."', style='dim')
        continue

    file_path, line = _line.split(':', 1)
    file_path = Path(file_path)
    reply_match = REPLY_REGEX.search(line)

    if is_debug:
        console.print(f"Checking line: '{line}'", style='dim')

    if reply_match:
        matches += 1

        if is_debug:
            console.print(f'  -> Matched...', style='bright_green')
    else:
        failures += 1
        console.print(Text('').append(f'  -> Failed: ', style='red3').append(f"'{line}'", style='cyan').append(f" (file: '{file_path.name}')", style='dim'))


console.print(
    f"\n\nMatched {matches} of {len(lines)} potential signatuares, [red]{failures}[/red] failures.",
    style='bright_white bold'
)

#console.print("(Previously 139 of 1787 failures)\n", style='dim')
