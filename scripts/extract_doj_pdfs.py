#!/usr/bin/env python
# Extract PDFs from the DOJ 2026-01-30 dump.
import logging
from logging import Formatter, Handler

from pdfalyzer.decorators.pdf_file import PdfFile
from yaralyzer.util.helpers.interaction_helper import ask_to_proceed
from yaralyzer.util.helpers.shell_helper import ShellResult

from epstein_files.documents.document import DATASET_NUMBER_REGEX, Document
from epstein_files.util.env import DOJ_2026_01_30_DIR, DOJ_2026_01_30_EXTRACTED_TEXT_DIR, DOJ_2026_01_30_DIR_ENV_VAR_NAME
from epstein_files.util.logging import logger
from epstein_files.util.rich import console

assert DOJ_2026_01_30_DIR is not None, f"{DOJ_2026_01_30_DIR_ENV_VAR_NAME} env var is not set!"
assert DOJ_2026_01_30_EXTRACTED_TEXT_DIR is not None

EXTRACT_ARGS = ['extract_pdf_text', '--no-page-number-panels', '--panelize-image-text']

if not DOJ_2026_01_30_EXTRACTED_TEXT_DIR.exists():
    ask_to_proceed(f"Dir {DOJ_2026_01_30_EXTRACTED_TEXT_DIR} doesn't exist, create?")
    DOJ_2026_01_30_EXTRACTED_TEXT_DIR.mkdir()


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


for dir in [d for d in DOJ_2026_01_30_DIR.glob('*') if d.is_dir()]:
    if (dir_match := DATASET_NUMBER_REGEX.search(dir.name)):
        dataset_number = int(dir_match.group(1))
        logger.info(f"Processing DataSet {dataset_number} (dir: '{dir}')")
    else:
        logger.debug(f"Skipping dir: '{dir}'")
        continue

    extracted_text_dir = DOJ_2026_01_30_EXTRACTED_TEXT_DIR.joinpath(dir.name)

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
