#!/usr/bin/env python
import re
from pathlib import Path
from subprocess import run

from dotenv import load_dotenv
load_dotenv()
from rich.text import Text

from epstein_files.documents.emails.constants import REPLY_REGEX
from epstein_files.output.rich import console
from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_PREFIX
from epstein_files.util.env import DOCS_DIR, args

FILE_PREFIX_LENGTH = len(HOUSE_OVERSIGHT_PREFIX) + 10
MIN_LINE_LENGTH = FILE_PREFIX_LENGTH + 14
MAX_LINE_LENGTH = FILE_PREFIX_LENGTH + 170


cmd = f'egrep -i "^(On|In a message dated) .*" {DOCS_DIR}/*.txt'
print(f"egrep command: '{cmd}'")
results = run(cmd, shell=True, capture_output=True, text=True, check=True).stdout

if args.deep_debug:
    print("\n\ncommand results:\n", results)

lines = [l.strip().removeprefix(str(DOCS_DIR)) for l in results.split('\n') if len(l.strip()) > 0]
print(f"Found {len(lines)} potential reply lines to check...")
matches = 0
failures = 0

for _line in lines:
    if len(_line) < MIN_LINE_LENGTH or _line.endswith('.ichat'):
        console.print(f'  -> Skipping empty, short, or ichat line: "{_line}"', style='dim')
        continue
    elif len(_line) > MAX_LINE_LENGTH:
        console.print(f'  -> Skipping long line: "{_line[0:90]}..."', style='dim')
        continue

    file_path, line = _line.split(':', 1)
    reply_match = REPLY_REGEX.search(line)
    file_path = Path(file_path)

    if args.debug:
        console.print(f"Checking line: '{line}'", style='dim')

    if reply_match:
        matches += 1

        if args.debug:
            console.print(f'  -> Matched...', style='bright_green')
    else:
        failures += 1
        txt = Text('').append(f'  -> Failed: ', style='red3').append(f"'{line}'", style='cyan')
        console.print(txt.append(f" (file: '{file_path.name}')", style='dim'))

console.print(
    f"\n\nMatched {matches} of {len(lines)} potential signatuares, [red]{failures}[/red] failures.",
    style='bright_white bold'
)

console.print(f"Previously matched 4631 of 6997 potential signatuares, 2366 failures.", style='dim')
