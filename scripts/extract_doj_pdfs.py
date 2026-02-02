#!/usr/bin/env python
# Extract PDFs from the DOJ 2026-01-30 dump.
# Requires the EPSTEIN_DOJ_PDFS_20260130_DIR env var to be set.
import logging
from logging import Formatter, Handler

from pdfalyzer.decorators.pdf_file import PdfFile
from yaralyzer.util.helpers.interaction_helper import ask_to_proceed
from yaralyzer.util.helpers.shell_helper import ShellResult

from epstein_files.documents.doj_file import DATASET_ID_REGEX
from epstein_files.util.env import DOJ_PDFS_20260130_DIR, DOJ_TXTS_20260130_DIR, DOJ_PDFS_20260130_DIR_ENV_VAR
from epstein_files.util.logging import logger
from epstein_files.util.rich import console

assert DOJ_PDFS_20260130_DIR is not None, f"{DOJ_PDFS_20260130_DIR_ENV_VAR} env var is not set!"
assert DOJ_TXTS_20260130_DIR is not None

EXTRACT_ARGS = ['extract_pdf_text', '--no-page-number-panels', '--panelize-image-text']

if not DOJ_TXTS_20260130_DIR.exists():
    ask_to_proceed(f"Dir {DOJ_TXTS_20260130_DIR} doesn't exist, create?")
    DOJ_TXTS_20260130_DIR.mkdir()


logger.setLevel(logging.DEBUG)
print(f"logger name = '{logger.name}', handlers = {logger.handlers}")

for app_name in ['pdfalyzer', 'yaralyzer']:
    app_log = logging.getLogger(app_name)

    for log in [app_log] + app_log.handlers:
        log.setLevel(logging.DEBUG)

        if isinstance(log, Handler):
            log.formatter = Formatter("[%(name)s] %(message)s")
        else:
            print(f"logger name = '{log.name}', handlers = {log.handlers}")


for dir in [d for d in DOJ_PDFS_20260130_DIR.glob('*') if d.is_dir()]:
    if (dir_match := DATASET_ID_REGEX.search(dir.name)):
        dataset_number = int(dir_match.group(1))
        logger.info(f"Processing DataSet {dataset_number} (dir: '{dir}')")
    else:
        logger.debug(f"Skipping dir: '{dir}'")
        continue

    extracted_text_dir = DOJ_TXTS_20260130_DIR.joinpath(dir.name)

    if not extracted_text_dir.exists():
        logger.warning(f"Export dir '{extracted_text_dir}' does not exist, creating...")
        extracted_text_dir.mkdir()

    for pdf_path in dir.glob('**/*.pdf'):
        txt_file_path = extracted_text_dir.joinpath(pdf_path.stem + '.txt')

        if txt_file_path.exists():
            logger.warning(f"Skipping file that already exists '{pdf_path}' in .txt format...")
            continue

        pdf_file = PdfFile(pdf_path)
        cmd = EXTRACT_ARGS + [str(pdf_path), '--output-dir', str(extracted_text_dir)]
        logger.debug(f"Processing file ({pdf_file.file_size / 1024:.1f} kb): '{pdf_path}': ")
        console.print(f"        " + ' '.join(cmd), style='wheat4')
        result = ShellResult.from_cmd(cmd, verify_success=True)
        logger.debug(result.output_logs(), extra={"highlighter": None})
        console.line()
