import re
from os import environ
from pathlib import Path
from sys import exit

from epstein_files.util.constant.strings import FILE_NAME_REGEX, FILE_STEM_REGEX, HOUSE_OVERSIGHT_PREFIX

EPSTEIN_DOCS_DIR_ENV_VAR_NAME = 'EPSTEIN_DOCS_DIR'
DOCS_DIR_ENV = environ[EPSTEIN_DOCS_DIR_ENV_VAR_NAME]
DOCS_DIR = Path(DOCS_DIR_ENV or '').resolve()

if not DOCS_DIR_ENV:
    print(f"ERROR: {EPSTEIN_DOCS_DIR_ENV_VAR_NAME} env var not set!")
    exit(1)
elif not DOCS_DIR.exists():
    print(f"ERROR: {EPSTEIN_DOCS_DIR_ENV_VAR_NAME}='{DOCS_DIR}' does not exist!")
    exit(1)

EXTRACTED_EMAILS_DIR = Path('emails_extracted_from_legal_filings')
FILE_ID_REGEX = re.compile(fr".*{FILE_NAME_REGEX.pattern}")
FILENAME_LENGTH = len(HOUSE_OVERSIGHT_PREFIX) + 6
KB = 1024
MB = KB * KB


# Handles both string and int 'id' args.
id_str = lambda id: f"{int(id):06d}"
filename_for_id = lambda id: file_stem_for_id(id) + '.txt'


def coerce_file_stem(filename_or_id: int | str) -> str:
    """Generate a valid file_stem no matter what form the argument comes in."""
    if isinstance(filename_or_id, str) and filename_or_id.startswith(HOUSE_OVERSIGHT_PREFIX):
        file_id = extract_file_id(filename_or_id)
        file_stem = file_stem_for_id(file_id)
    else:
        file_stem = file_stem_for_id(filename_or_id)

    if not FILE_STEM_REGEX.match(file_stem):
        raise RuntimeError(f"Invalid stem '{file_stem}' from '{filename_or_id}'")

    return file_stem


def coerce_file_name(filename_or_id: int | str) -> str:
    return coerce_file_stem(filename_or_id) + '.txt'


def coerce_file_path(filename_or_id: int | str) -> Path:
    return DOCS_DIR.joinpath(coerce_file_name(filename_or_id))


def extract_file_id(filename_or_id: int | str | Path) -> str:
    if isinstance(filename_or_id, int) or (isinstance(filename_or_id, str) and len(filename_or_id) <= 6):
        return id_str(filename_or_id)

    file_match = FILE_ID_REGEX.match(str(filename_or_id))

    if not file_match:
        raise RuntimeError(f"Failed to extract file ID from {filename_or_id}")

    return file_match.group(1)


def file_size(file_path: str | Path) -> int:
    return Path(file_path).stat().st_size


def file_size_str(file_path: str | Path) -> str:
    size = file_size(file_path)
    digits = 2

    if size > MB:
        size_num = float(size) / MB
        size_str = 'MB'
    elif size > KB:
        size_num = float(size) / KB
        size_str = 'kb'
        digits = 1
    else:
        return f"{size} b"

    return f"{size_num:,.{digits}f} {size_str}"


def file_stem_for_id(id: int | str) -> str:
    if isinstance(id, int) or (isinstance(id, str) and len(id) <= 6):
        return f"{HOUSE_OVERSIGHT_PREFIX}{id_str(id)}"
    elif len(id) == 8:
        return f"{HOUSE_OVERSIGHT_PREFIX}{id}"
    else:
        raise RuntimeError(f"Unknown kind of file id {id}")


def is_local_extract_file(filename) -> bool:
    """Return true if filename is of form 'HOUSE_OVERSIGHT_029835_1.txt'."""
    file_match = FILE_ID_REGEX.match(str(filename))
    return True if file_match and file_match.group(2) else False
