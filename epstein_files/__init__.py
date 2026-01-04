#!/usr/bin/env python
"""
Reformat Epstein text message files for readability and count email senders.
For use with iMessage log files from https://drive.google.com/drive/folders/1hTNH5woIRio578onLGElkTWofUSWRoH_

Install: 'poetry install'
    Run: 'EPSTEIN_DOCS_DIR=/path/to/TXT ./generate.py'
"""
from sys import exit

from dotenv import load_dotenv
load_dotenv()

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.constant.html import *
from epstein_files.util.constant.names import *

from epstein_files.util.env import args
from epstein_files.util.file_helper import GH_PAGES_HTML_PATH, make_clean
from epstein_files.util.logging import logger
from epstein_files.util.output import print_emails, print_json_metadata, print_json_stats, print_text_messages
from epstein_files.util.rich import print_header, write_html
from epstein_files.util.timer import Timer


def generate_html() -> None:
    if args.make_clean:
        make_clean()
        exit()

    timer = Timer()
    epstein_files = EpsteinFiles.get_files(timer)

    if args.json_metadata:
        print_json_metadata(epstein_files)
        exit()

    print_header(epstein_files)

    if args.colors_only:
        exit()

    if args.output_texts:
        print_text_messages(epstein_files)
        timer.print_at_checkpoint(f'Printed {len(epstein_files.imessage_logs)} text message logs')

    if args.output_emails:
        emails_printed = print_emails(epstein_files)
        timer.print_at_checkpoint(f"Printed {emails_printed:,} emails")

    if args.output_other_files:
        files_printed = epstein_files.print_other_files_table()
        timer.print_at_checkpoint(f"Printed {len(files_printed)} other files")

    # Save output
    write_html(GH_PAGES_HTML_PATH)
    logger.warning(f"Total time: {timer.seconds_since_start_str()}")

    # JSON stats (mostly used for building pytest checks)
    if args.json_stats:
        print_json_stats(epstein_files)
