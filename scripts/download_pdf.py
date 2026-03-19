#!/usr/bin/env python
from epstein_files.people.names import *
from epstein_files.util.constant.urls import download_jmail_pdf
from epstein_files.util.env import args
from epstein_files.util.helpers.file_helper import extract_file_id, open_file_or_url
from epstein_files.util.helpers.string_helper import INTEGER_REGEX
from epstein_files.util.logging import exit_with_error, logger


if len(args.positional_args) != 2:
    exit_with_error(f"two positional args expected (ID and dataset number)")
elif not INTEGER_REGEX.match(args.positional_args[1]):
    exit_with_error(f"2nd argument should be a number, instead it's {args.positional_args[1]}")

file_id = extract_file_id(args.positional_args[0].upper())
data_set_id = int(args.positional_args[1])
pdf_path = download_jmail_pdf(file_id, data_set_id)

if True or args.open_txt:
    open_file_or_url(pdf_path)
