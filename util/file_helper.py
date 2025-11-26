import re
from os import environ
from pathlib import Path

DOCS_DIR_ENV = environ['EPSTEIN_DOCS_DIR']
HOUSE_OVERSIGHT_PREFIX = 'HOUSE_OVERSIGHT_'

if not DOCS_DIR_ENV:
    raise EnvironmentError(f"EPSTEIN_DOCS_DIR env var not set!")

DOCS_DIR = Path(DOCS_DIR_ENV).resolve()
JSON_FILES_SUBDIR = 'json_files'
JSON_DIR = DOCS_DIR.joinpath(JSON_FILES_SUBDIR)
OUTPUT_GH_PAGES_HTML = Path('docs').joinpath('index.html')
FILE_ID_REGEX = re.compile(rf'.*{HOUSE_OVERSIGHT_PREFIX}(\d+)(\.txt)?')


def extract_file_id(filename) -> str:
    file_match = FILE_ID_REGEX.match(str(filename))

    if file_match:
        return file_match.group(1)
    else:
        raise RuntimeError(f"Failed to extract file ID from {filename}")


def move_json_file(file_arg: Path):
    json_subdir_path = JSON_DIR.joinpath(file_arg.name + '.json')
    print(f"'{file_arg}' looks like JSON, moving to '{json_subdir_path}'\n")
    file_arg.rename(json_subdir_path)
