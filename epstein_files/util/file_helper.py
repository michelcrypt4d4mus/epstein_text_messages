import re
from os import environ
from pathlib import Path
from sys import exit

from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_PREFIX

EPSTEIN_DOCS_DIR_ENV_VAR_NAME = 'EPSTEIN_DOCS_DIR'
DOCS_DIR_ENV = environ[EPSTEIN_DOCS_DIR_ENV_VAR_NAME]
DOCS_DIR = Path(DOCS_DIR_ENV or '').resolve()

if not DOCS_DIR_ENV:
    print(f"ERROR: {EPSTEIN_DOCS_DIR_ENV_VAR_NAME} env var not set!")
    exit(1)
elif not DOCS_DIR.exists():
    print(f"ERROR: {EPSTEIN_DOCS_DIR_ENV_VAR_NAME}='{DOCS_DIR}' does not exist!")
    exit(1)

JSON_DIR = DOCS_DIR.joinpath('json_files')
HTML_DIR = Path('docs')
EXTRACTED_EMAILS_DIR = Path('emails_extracted_from_legal_filings')
GH_PAGES_HTML_PATH = HTML_DIR.joinpath('index.html')
WORD_COUNT_HTML_PATH = HTML_DIR.joinpath('epstein_emails_word_count.html')
EPSTEIN_WORD_COUNT_HTML_PATH = HTML_DIR.joinpath('epstein_texts_and_emails_word_count.html')
PICKLED_PATH = Path("the_epstein_files.pkl.gz")

FILE_STEM_REGEX = re.compile(fr"{HOUSE_OVERSIGHT_PREFIX}(\d{{6}})")
FILE_ID_REGEX = re.compile(fr".*{FILE_STEM_REGEX.pattern}(_\d{1,2})?(\.txt(\.json)?)?")
FILENAME_LENGTH = len(HOUSE_OVERSIGHT_PREFIX) + 6
KB = 1024
MB = KB * KB


def build_filename_for_id(id: str | int, include_txt_suffix: bool = False) -> str:
    return f"{HOUSE_OVERSIGHT_PREFIX}{int(id):06d}" + ('.txt' if include_txt_suffix else '')


def build_file_stem(filename_or_id: int | str) -> str:
    if isinstance(filename_or_id, str) and filename_or_id.startswith(HOUSE_OVERSIGHT_PREFIX):
        file_stem = str(filename_or_id)
    else:
        file_stem = build_filename_for_id(filename_or_id)

    if not FILE_STEM_REGEX.match(file_stem):
        raise RuntimeError(f"Built invalid file stem '{file_stem}' from filename_or_id={filename_or_id} (pattern='{FILE_STEM_REGEX.pattern}')")

    return file_stem


def extract_file_id(filename: str | Path) -> str:
    file_match = FILE_ID_REGEX.match(str(filename))

    if file_match:
        return file_match.group(1)
    else:
        raise RuntimeError(f"Failed to extract file ID from {filename}")


def file_size_str(file_path: str | Path) -> str:
    file_size = float(Path(file_path).stat().st_size)

    if file_size > MB:
        size_num = file_size / MB
        size_str = 'MB'
    elif file_size > KB:
        size_num = file_size / KB
        size_str = 'kb'
    else:
        size_num = file_size
        size_str = 'bytes'

    return f"{size_num:,.2f} {size_str}"


def is_local_extract_file(filename) -> bool:
    """Return true if filename is of form 'HOUSE_OVERSIGHT_029835_1.txt'."""
    file_match = FILE_ID_REGEX.match(str(filename))
    return True if file_match and file_match.group(2) else False


def move_json_file(file_arg: Path):
    json_subdir_path = JSON_DIR.joinpath(file_arg.name + '.json')
    print(f"'{file_arg}' looks like JSON, moving to '{json_subdir_path}'\n")
    file_arg.rename(json_subdir_path)
