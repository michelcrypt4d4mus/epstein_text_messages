import re
from pathlib import Path

from util.file_helper import load_file
from util.emails import BAD_EMAILER_REGEX, BROKEN_EMAIL_REGEX, DETECT_EMAIL_REGEX, extract_email_sender

FILE_DIR = Path('/Users/stardestroyer/Screenshots/epstein_files/raw/TEXT/001_text_logs')


basename = 'HOUSE_OVERSIGHT_027094.txt'
file_text = load_file(FILE_DIR.joinpath(basename))
file_lines = file_text.split('\n')
print('\n'.join(file_lines[0:15]))

m = BROKEN_EMAIL_REGEX.search(file_text)
