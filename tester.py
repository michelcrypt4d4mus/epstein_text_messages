import re
from pathlib import Path
from util.file_helper import load_file

FILE_DIR = Path('/Users/stardestroyer/Screenshots/epstein_files/raw/TEXT/001_text_logs')
basename = 'HOUSE_OVERSIGHT_028789.txt'

txt = load_file(FILE_DIR.joinpath(basename))
file_lines = txt.split('\n')
