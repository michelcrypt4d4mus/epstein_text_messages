#!/usr/bin/env python
import re
from pathlib import Path
from subprocess import run

from dotenv import load_dotenv
load_dotenv()
from rich.console import Console

from epstein_files.documents.emails.constants import SENT_FROM_REGEX
from epstein_files.util.env import DOCS_DIR, args


console = Console(color_system='256')
cmd = f'egrep -i "Sent (by|from|via) " {DOCS_DIR}/*.txt'
print(f"DOCS_DIR='{DOCS_DIR.resolve()}'")
print(f"Command: {cmd}")
results = run(cmd, shell=True, capture_output=True, text=True, check=True).stdout

if args.debug:
    print("\n\ncommand results:\n", results)

lines = [l.strip() for l in results.split('\n') if len(l.strip()) > 0]
print(f"Found {len(lines)} potential Sent by [device] lines to check...")
signatures = set()
matches = 0
failures = 0


for _line in lines:
    line = _line.strip().removeprefix(str(DOCS_DIR))

    if not line:
        console.print(f'Skipping empty line? "{_line}"')
        continue
    elif args.debug:
        console.print(f"Checking line: '{line}'", style='dim')

    file_path, line = line.split(':', 1)
    file_path = Path(file_path)
    signature_match = SENT_FROM_REGEX.search(line)

    if signature_match:
        signature = signature_match.group(0)
        signatures.add(signature)
        matches += 1

        if args.debug:
            console.print(f'Matched signature "{signature}" in line "{line}"', style='cyan')
    else:
        if line.startswith('>'):
            console.print(f'Failed to match in quoted line "{file_path.name}": "{line.strip()}"', style='dim')
        else:
            console.print(f'Failed to match line: "{line.strip()}" (file: "{file_path.name}")', style='red3')

        failures += 1


console.print(
    f"\n\nMatched {matches} of {len(lines)} potential signatuares, [red]{failures}[/red] failures.",
    style='bright_white bold'
)

console.print("(Previously 139 of 1787 failures)\n", style='dim')
console.print(f"All matched signatures: \n\n   * " + '\n   * '.join(sorted(signatures)))
