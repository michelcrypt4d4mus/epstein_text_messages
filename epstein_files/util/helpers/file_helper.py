import re
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from subprocess import check_output, run
from typing import Generator

from rich.panel import Panel
from rich.text import Text

from epstein_files.output.html.html_dir import DOC_IMAGES_DIR, HtmlDir
from epstein_files.util.constant.strings import (DOJ_FILE_STEM_REGEX, DOJ_FILE_NAME_REGEX,
     EFTA_PREFIX, FILE_ID_PATTERN, HOUSE_OVERSIGHT_2025_FILENAME_REGEX,
     HOUSE_OVERSIGHT_2025_FILE_STEM_REGEX, HOUSE_OVERSIGHT_2025_ID_REGEX, HOUSE_OVERSIGHT_PREFIX,
     LOCAL_EXTRACT_REGEX)
from epstein_files.util.env import DOCS_DIR, DOJ_PDFS_20260130_DIR, DOJ_TXTS_20260130_DIR, DROPSITE_EMLS_DIR
from epstein_files.util.helpers.env_helpers import get_env_dir
from epstein_files.util.helpers.string_helper import is_integer, join_patterns
from epstein_files.util.logging import logger

BROKEN_PDFS_DIR = get_env_dir('BROKEN_PDFS_DIR', must_exist=False)
PROJECT_DIR = Path(__file__).parent.parent.parent.parent
RESEARCH_DATA_REPO_DIR = PROJECT_DIR.parent.parent.joinpath('Epstein-research-data')
EXTRACTED_EMAILS_DIR = PROJECT_DIR.joinpath('emails_extracted_from_legal_filings')

DOJ_FILE_ID_REGEX = re.compile(fr".*{DOJ_FILE_NAME_REGEX.pattern}")
DROPSITE_FILE_NAME_REGEX = re.compile(fr"{DROPSITE_EMLS_DIR}.* (\d\d\d\d-\d\d-\d\d \d+)\.eml")
HOUSE_FILE_ID_REGEX = re.compile(fr".*{HOUSE_OVERSIGHT_2025_FILENAME_REGEX.pattern}")
VALID_ID_REGEX = re.compile(fr"^({FILE_ID_PATTERN})$")

FILENAME_LENGTH = len(HOUSE_OVERSIGHT_PREFIX) + 6  # TODO: this is obsolete
DIFF_COLORS = ['spring_green4', 'sea_green1']
DIFF_PFXES = ['<', '>']
KB = 1_024
MB = KB * KB

IMG_EXTENSIONS = [
    'gif',
    'jpeg',
    'jpg',
    'png',
    'webp',
]

# File stat helpers
file_size = lambda file_path: Path(file_path).stat().st_size
is_valid_id = lambda id: bool(VALID_ID_REGEX.match(id))
modified_at = lambda file_path: datetime.fromtimestamp(Path(file_path).stat().st_mtime)

# Document path helpers
all_txt_paths = lambda: doj_txt_paths() + oversight_txt_paths() + dropsite_eml_paths()
doj_txt_paths = lambda: [f for f in DOJ_TXTS_20260130_DIR.glob('**/*.txt')] if DOJ_TXTS_20260130_DIR else []
dropsite_eml_paths = lambda: [f for f in DROPSITE_EMLS_DIR.glob('*.eml')]
oversight_txt_paths = lambda: [f for f in DOCS_DIR.iterdir() if f.is_file() and not f.name.startswith('.')]


def broken_pdfs_dir() -> Path:
    """Location of broken PDFs, if env var is set."""
    assert BROKEN_PDFS_DIR, f"BROKEN_PDFS_DIR not set!"
    return BROKEN_PDFS_DIR


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
    # logger.debug(f"coerce_file_stem(): {filename_or_id}")

    if isinstance(filename_or_id, str) and (is_doj_file(filename_or_id) or is_picture(str(filename_or_id))):
        return Path(filename_or_id).stem
    elif isinstance(filename_or_id, Path):
        return filename_or_id.stem

    if isinstance(filename_or_id, str) and filename_or_id.startswith(HOUSE_OVERSIGHT_PREFIX):
        file_id = extract_file_id(filename_or_id)
        file_stem = house_file_stem(file_id)
    else:
        file_stem = house_file_stem(str(filename_or_id))

    if not HOUSE_OVERSIGHT_2025_FILE_STEM_REGEX.match(file_stem):
        raise RuntimeError(f"Invalid stem '{file_stem}' from '{filename_or_id}'")

    return file_stem


def coerce_url_slug(filename_or_id: int | str | Path) -> str:
    file_stem = coerce_file_stem(filename_or_id)

    if is_local_extract_file(file_stem):
        return LOCAL_EXTRACT_REGEX.sub('', file_stem)
    else:
        return file_stem


def diff_files(file1: str | Path, file2: str | Path, print_to_console: bool = True) -> str:
    """Run shell `diff` for two files."""
    cmd = f"diff '{file1}' '{file2}'"
    logger.warning(f"Running diff cmd: '{cmd}'")
    diff_result = run(cmd, shell=True, capture_output=True, text=True).stdout

    if print_to_console:
        _print_colored_diff_output(diff_result, [file1, file2])

    return diff_result


def extract_efta_id(file_id: str) -> int:
    return int(file_id.removeprefix(EFTA_PREFIX))


def extract_file_id(filename_or_id: int | str | Path) -> str:
    """DOJ 2026-01 files have different pattern."""
    if isinstance(filename_or_id, (str, Path)) and is_file_id_the_file_stem(Path(filename_or_id)):
        return Path(filename_or_id).stem
    # elif isinstance(filename_or_id, str) and filename_or_id.startswith('DropSite'):
    #     return filename_or_id
    elif isinstance(filename_or_id, (str, Path)) and (m := DROPSITE_FILE_NAME_REGEX.match(str(filename_or_id))):
        return f"DropSite {m.group(1)}"
    elif isinstance(filename_or_id, str):
        filename_or_id = filename_or_id.removesuffix(',')  # clean up commas from bad args.positional_args copypasta

    filename_str = str(filename_or_id)

    if is_integer(filename_str):
        return format_house_oversight_id(filename_str)
    elif (id_match := HOUSE_OVERSIGHT_2025_ID_REGEX.search(filename_str.upper())):
        return id_match.group(1)
    else:
        logger.error(f"filename_str='{filename_str}', HOUSE_FILE_ID_REGEX='{HOUSE_FILE_ID_REGEX.pattern}'")
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


def format_house_oversight_id(id: int | str) -> str:
    """Make sure there's enough leading zeroes for 6 digit ID."""
    return f"{int(id):06d}"


def house_file_stem(id: int | str) -> str:
    if is_integer(id):
        return f"{HOUSE_OVERSIGHT_PREFIX}{format_house_oversight_id(id)}"
    elif HOUSE_OVERSIGHT_2025_ID_REGEX.match(id):
        return f"{HOUSE_OVERSIGHT_PREFIX}{id}"
    else:
        raise ValueError(f"Unknown kind of file id {id}")


def is_doj_file(file: str | Path) -> bool:
    """Check for EFTAXXXXXXX style files."""
    return bool(DOJ_FILE_STEM_REGEX.search(str(file)))


def is_file_id_the_file_stem(file_path: Path) -> bool:
    return is_doj_file(file_path) or str(DOC_IMAGES_DIR) in str(file_path)


def is_house_oversight_file(file: str | Path) -> bool:
    return bool(HOUSE_OVERSIGHT_2025_FILE_STEM_REGEX.search(str(file)))


def is_local_extract_file(filename: str | Path) -> bool:
    """Return True if `filename` is of form 'HOUSE_OVERSIGHT_029835_1.txt'."""
    match = HOUSE_FILE_ID_REGEX.search(str(filename)) or DOJ_FILE_ID_REGEX.search(str(filename))
    return True if match and match.group(2) else False


def is_picture(file_name: str | Path) -> bool:
    return any(str(file_name).endswith(ext) for ext in IMG_EXTENSIONS)  # or 'Epstein_and_MBS' in file_name


@contextmanager
def jmail_download_bad_ids() -> Generator[set[str], None, None]:
    """Track file IDs that don't download correctly when pulled from Jmail via constructed URLs."""
    known_bad_jmail_ids_path = broken_pdfs_dir().joinpath('broken_jmail_ids.txt')
    known_bad_jmail_ids_bak_path = Path(str(known_bad_jmail_ids_path) + '.bak')

    try:
        if known_bad_jmail_ids_path.exists():
            known_bad_ids = set(known_bad_jmail_ids_path.read_text().strip().split('\n'))
            logger.warning(f"Loaded {len(known_bad_ids)} known bad IDs from '{known_bad_jmail_ids_path}'...")
            shutil.copy(known_bad_jmail_ids_path, known_bad_jmail_ids_bak_path)
        else:
            known_bad_ids = set([])

        yield known_bad_ids
    finally:
        known_bad_jmail_ids_path.write_text('\n'.join(known_bad_ids))
        logger.warning(f"Wrote {len(known_bad_ids)} known bad IDs to '{known_bad_jmail_ids_path}'")


def local_doj_file_path(id: str, data_set_id: int) -> Path:
    """Build a path to a DOj PDF on the local filesystem."""
    return DOJ_PDFS_20260130_DIR.joinpath(f"DataSet {data_set_id}", f"{id}.pdf")


def log_file_write(file_path: str | Path) -> None:
    logger.warning(f"Wrote {file_size_str(file_path)} to '{file_path}'")


def open_file_or_url(thing_to_open: str | Path) -> None:
    """Use `open` shell command to open `thing_to_open` (usually a local path or URL)."""
    logger.info(f"opening '{thing_to_open}'")
    cmd = 'code' if str(thing_to_open).endswith('.txt') else 'open'
    check_output([cmd, str(thing_to_open)])


def relative_to_project_dir(_path: str | Path) -> Path:
    path = Path(_path)
    return path.relative_to(PROJECT_DIR) if path.is_absolute() else path


def _print_colored_diff_output(diff_result: str, files: list[str | Path]) -> list[Text]:
    """Color the output of shell `diff` execution."""
    from epstein_files.output.rich import console

    panel_file_txts = [
        Text(f"{DIFF_PFXES[i]} ").append(f"file{i + 1}: ", 'dim').append(str(relative_to_project_dir(f)), DIFF_COLORS[i])
        for i, f in enumerate(files)
    ]

    console.print('\n', Panel(Text('\n').join(panel_file_txts), expand=False))
    diff_line_txts = []

    for line in diff_result.split('\n'):
        if line.startswith(DIFF_PFXES[0]):
            style = DIFF_COLORS[0]
        elif line.startswith(DIFF_PFXES[1]):
            style = DIFF_COLORS[1]
        else:
            style='dim'

        diff_line_txts.append(Text(line, style=style))
        console.print(diff_line_txts[-1])

    return diff_line_txts
