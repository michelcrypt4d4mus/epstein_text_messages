#!/usr/bin/env python
# Extract PDFs from the DOJ 2026-01-30 dump.
# Requires the EPSTEIN_DOJ_PDFS_20260130_DIR env var to be set.
import re
import shutil
import sys

from pdfalyzer.decorators.pdf_file import PdfFile
from rich.prompt import Confirm, Prompt
from yaralyzer.util.helpers.interaction_helper import ask_to_proceed
from yaralyzer.util.helpers.shell_helper import ShellResult

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.documents.document import DOJ_DATASET_ID_REGEX
from epstein_files.output.rich import console
from epstein_files.util.constant.strings import DOJ_FILE_NAME_REGEX
from epstein_files.util.env import DOJ_PDFS_20260130_DIR, DOJ_TXTS_20260130_DIR, DOJ_PDFS_20260130_DIR_ENV_VAR, args
from epstein_files.util.helpers.env_helpers import get_env_dir
from epstein_files.util.logging import logger

assert DOJ_PDFS_20260130_DIR is not None, f"{DOJ_PDFS_20260130_DIR_ENV_VAR} env var is not set!"
assert DOJ_TXTS_20260130_DIR is not None

BROKEN_PDFS_DIR = get_env_dir('BROKEN_PDFS_DIR', must_exist=True)
JMAIL_FILENAME_REGEX = re.compile(r"vol(\d+)-(?:official-doj-latest-)?(efta\d+)(-pdf)?.pdf")
BAD_FILENAME_REGEX = re.compile(r".*/EFTA\d+-\d\.pdf")
EXTRACT_ARGS = ['extract_pdf_text', '--no-page-number-panels', '--panelize-image-text']


if not DOJ_TXTS_20260130_DIR.exists():
    ask_to_proceed(f"Dir {DOJ_TXTS_20260130_DIR} doesn't exist, create?")
    DOJ_TXTS_20260130_DIR.mkdir()

skipped = 0

for dir in [d for d in DOJ_PDFS_20260130_DIR.glob('*') if d.is_dir()]:
    if (dir_match := DOJ_DATASET_ID_REGEX.search(dir.name)):
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
        if (jmail_match := JMAIL_FILENAME_REGEX.match(pdf_path.name)):
            new_pdf_path = pdf_path.parent.joinpath(jmail_match.group(2).upper() + '.pdf')
            logger.warning(f"Found Jmail PDF '{pdf_path}'\n      moving to '{new_pdf_path}'")
            shutil.move(pdf_path, new_pdf_path)
            pdf_path = new_pdf_path
        elif not DOJ_FILE_NAME_REGEX.match(pdf_path.name):
            raise RuntimeError(f"Bad filename '{pdf_path}'!")

        txt_file_path = extracted_text_dir.joinpath(pdf_path.stem + '.txt')

        if txt_file_path.exists():
            logger.info(f"Skipping file that already exists '{pdf_path}' in .txt format...")

            if skipped > 0 and skipped % 500 == 0:
                logger.warning(f"Skipped {skipped} PDFs that already exist as .txt...")

            skipped += 1
            continue

        pdf_file = PdfFile(pdf_path)
        cmd = EXTRACT_ARGS + [str(pdf_path), '--output-dir', str(extracted_text_dir)]
        logger.debug(f"Processing file ({pdf_file.file_size / 1024:.1f} kb): '{pdf_path}': ")
        console.print(f"        " + ' '.join(cmd), style='wheat4')
        result = ShellResult.from_cmd(cmd, verify_success=True)
        logger.debug(result.output_logs(), extra={"highlighter": None})
        console.line()

        if not txt_file_path.exists():
            if pdf_path.read_text().startswith('<!DOCTYPE html>'):
                logger.error(f"{pdf_path} is an HTML file, not a PDF, moving to '{BROKEN_PDFS_DIR}'...")
            else:
                logger.error(f"Failed to extract any text from {pdf_path}, moving to '{BROKEN_PDFS_DIR}'...")

            shutil.move(pdf_path, BROKEN_PDFS_DIR.joinpath(pdf_path.name))

args.constantize = True
EpsteinFiles.get_files().load_new_files()
