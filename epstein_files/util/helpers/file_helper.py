import re
from pathlib import Path

from epstein_files.util.constant.strings import (DOJ_FILE_STEM_REGEX, EFTA_PREFIX,
     HOUSE_OVERSIGHT_NOV_2025_FILE_NAME_REGEX, HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX,
     HOUSE_OVERSIGHT_PREFIX, LOCAL_EXTRACT_REGEX)
from epstein_files.util.env import DOCS_DIR, DOJ_TXTS_20260130_DIR
from epstein_files.util.logging import logger

EXTRACTED_EMAILS_DIR = Path('emails_extracted_from_legal_filings')
FILE_ID_REGEX = re.compile(fr".*{HOUSE_OVERSIGHT_NOV_2025_FILE_NAME_REGEX.pattern}")
FILENAME_LENGTH = len(HOUSE_OVERSIGHT_PREFIX) + 6
KB = 1024
MB = KB * KB

all_txt_paths = lambda: doj_txt_paths() + oversight_txt_paths()
doj_txt_paths = lambda: [f for f in DOJ_TXTS_20260130_DIR.glob('**/*.txt')] if DOJ_TXTS_20260130_DIR else []
oversight_txt_paths = lambda: [f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]

file_size = lambda file_path: Path(file_path).stat().st_size


# Coerce methods handle both string and int arguments.
def coerce_file_name(filename_or_id: int | str | Path) -> str:
    return coerce_file_stem(filename_or_id) + '.txt'


def coerce_file_path(filename_or_id: int | str) -> Path:
    """Returns the `Path` for the file with `filename_or_id` ID."""
    filename = coerce_file_name(filename_or_id)

    if isinstance(filename_or_id, str) and is_doj_file(filename_or_id):
        for txt_file in DOJ_TXTS_20260130_DIR.glob('**/*.txt'):
            if txt_file.name == filename:
                return txt_file

        raise FileNotFoundError(f"'{filename_or_id}' looks like a DOJ file ID but no file named {filename} in '{DOJ_TXTS_20260130_DIR}'!")
    else:
        return DOCS_DIR.joinpath(filename)


def coerce_file_stem(filename_or_id: int | str | Path) -> str:
    """Generate a valid file stem no matter what form the argument comes in."""
    if isinstance(filename_or_id, str) and is_doj_file(filename_or_id):
        return Path(filename_or_id).stem
    elif isinstance(filename_or_id, Path):
        filename_or_id = filename_or_id.stem

    if isinstance(filename_or_id, str) and filename_or_id.startswith(HOUSE_OVERSIGHT_PREFIX):
        file_id = extract_file_id(filename_or_id)
        file_stem = file_stem_for_id(file_id)
    else:
        file_stem = file_stem_for_id(str(filename_or_id))

    if not HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX.match(file_stem):
        raise RuntimeError(f"Invalid stem '{file_stem}' from '{filename_or_id}'")

    return file_stem


def coerce_url_slug(filename_or_id: int | str | Path) -> str:
    file_stem = coerce_file_stem(filename_or_id)

    if is_local_extract_file(file_stem):
        return LOCAL_EXTRACT_REGEX.sub('', file_stem)
    else:
        return file_stem


def extract_efta_id(file_id: str) -> int:
    return int(file_id.removeprefix(EFTA_PREFIX))


def extract_file_id(filename_or_id: int | str | Path) -> str:
    # DOJ 2026-01 files have different pattern
    if isinstance(filename_or_id, (str, Path)) and is_doj_file(filename_or_id):
        return Path(filename_or_id).stem
    elif isinstance(filename_or_id, str):
        filename_or_id = filename_or_id.removesuffix(',')  # clean up commas from bad args.positional_args copypasta

    if isinstance(filename_or_id, int) or (isinstance(filename_or_id, str) and len(filename_or_id) <= 6):
        return format_house_oversight_id(filename_or_id)

    filename_str = str(filename_or_id)

    if len(filename_str) == 8 and filename_str.startswith('00'):
        return f"{HOUSE_OVERSIGHT_PREFIX}{filename_or_id}"
    elif (file_match := FILE_ID_REGEX.match(filename_str.upper())):
        return file_match.group(1)
    else:
        raise RuntimeError(f"Failed to extract file ID from '{filename_or_id}' (type: {type(filename_or_id).__name__}!")


def file_size_str(file_path: str | Path, digits: int | None = None):
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
        return f"{HOUSE_OVERSIGHT_PREFIX}{format_house_oversight_id(id)}"

    if len(id) == 8:
        return f"{HOUSE_OVERSIGHT_PREFIX}{id}"
    else:
        raise RuntimeError(f"Unknown kind of file id {id}")


def format_house_oversight_id(id: int | str) -> str:
    """Make sure there's enough leading zeroes for 6 digit ID."""
    return f"{int(id):06d}"


def is_doj_file(file: str | Path) -> bool:
    """Check for EFTAXXXXXXX style files."""
    return bool(DOJ_FILE_STEM_REGEX.search(str(file)))


def is_house_oversight_file(file: str | Path) -> bool:
    return bool(HOUSE_OVERSIGHT_NOV_2025_FILE_STEM_REGEX.search(str(file)))


def is_local_extract_file(filename) -> bool:
    """Return True if `filename` is of form 'HOUSE_OVERSIGHT_029835_1.txt'."""
    file_match = FILE_ID_REGEX.match(str(filename))
    return True if file_match and file_match.group(2) else False


def log_file_write(file_path: str | Path) -> None:
    logger.warning(f"Wrote {file_size_str(file_path)} to '{file_path}'")
