import re
from os import environ
from pathlib import Path
from sys import exit

from epstein_files.util.constant.strings import HOUSE_OVERSIGHT_PREFIX

EPSTEIN_DOCS_DIR_ENV_VAR_NAME = 'EPSTEIN_DOCS_DIR'
DOCS_DIR_ENV = environ[EPSTEIN_DOCS_DIR_ENV_VAR_NAME]

if not DOCS_DIR_ENV:
    print(f"ERROR: {EPSTEIN_DOCS_DIR_ENV_VAR_NAME} env var not set!")
    exit(1)

DOCS_DIR = Path(DOCS_DIR_ENV).resolve()
JSON_FILES_SUBDIR = 'json_files'
JSON_DIR = DOCS_DIR.joinpath(JSON_FILES_SUBDIR)
FILE_ID_REGEX = re.compile(rf'.*{HOUSE_OVERSIGHT_PREFIX}(\d+)(_\d+)?(\.txt)?')
OUTPUT_GH_PAGES_HTML = Path('docs').joinpath('index.html')


if not DOCS_DIR.exists():
    print(f"ERROR: {EPSTEIN_DOCS_DIR_ENV_VAR_NAME}='{DOCS_DIR}' does not exist!")
    exit(1)


def build_filename_for_id(id: str | int, include_txt_suffix: bool = False) -> str:
    id_str = f"{int(id):06d}"
    return f"{HOUSE_OVERSIGHT_PREFIX}{id_str}" + ('.txt' if include_txt_suffix else '')


def extract_file_id(filename) -> str:
    file_match = FILE_ID_REGEX.match(str(filename))

    if file_match:
        return file_match.group(1)
    else:
        raise RuntimeError(f"Failed to extract file ID from {filename}")


def is_local_extract_file(filename) -> bool:
    """Return true if filename is of form 'HOUSE_OVERSIGHT_029835_1.txt'."""
    file_match = FILE_ID_REGEX.match(str(filename))
    return True if file_match and file_match.group(2) else False


def move_json_file(file_arg: Path):
    json_subdir_path = JSON_DIR.joinpath(file_arg.name + '.json')
    print(f"'{file_arg}' looks like JSON, moving to '{json_subdir_path}'\n")
    file_arg.rename(json_subdir_path)
