import re
from pathlib import Path

from epstein_files.util.constant.strings import FILE_NAME_REGEX, FILE_STEM_REGEX, HOUSE_OVERSIGHT_PREFIX
from epstein_files.util.env import DOCS_DIR
from epstein_files.util.logging import logger

EXTRACTED_EMAILS_DIR = Path('emails_extracted_from_legal_filings')
FILE_ID_REGEX = re.compile(fr".*{FILE_NAME_REGEX.pattern}")
FILENAME_LENGTH = len(HOUSE_OVERSIGHT_PREFIX) + 6
KB = 1024
MB = KB * KB

file_size = lambda file_path: Path(file_path).stat().st_size

# Coerce methods handle both string and int arguments.
coerce_file_name = lambda filename_or_id: coerce_file_stem(filename_or_id) + '.txt'
coerce_file_path = lambda filename_or_id: DOCS_DIR.joinpath(coerce_file_name(filename_or_id))
id_str = lambda id: f"{int(id):06d}"


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


def extract_file_id(filename_or_id: int | str | Path) -> str:
    if isinstance(filename_or_id, int) or (isinstance(filename_or_id, str) and len(filename_or_id) <= 6):
        return id_str(filename_or_id)

    file_match = FILE_ID_REGEX.match(str(filename_or_id))

    if not file_match:
        raise RuntimeError(f"Failed to extract file ID from {filename_or_id}")

    return file_match.group(1)


def file_size_str(file_path, digits: int | None = None):
    return file_size_to_str(file_size(file_path), digits)


def file_size_to_str(size: int, digits: int | None = None) -> str:
    _digits = 2

    if size > MB:
        size_num = float(size) / MB
        size_str = 'MB'
    elif size > KB:
        size_num = float(size) / KB
        size_str = 'kb'
        _digits = 1
    else:
        return f"{size} b"

    digits = _digits if digits is None else digits
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


def log_file_write(file_path: str | Path) -> None:
    logger.warning(f"Wrote {file_size_str(file_path)} to '{file_path}'")
