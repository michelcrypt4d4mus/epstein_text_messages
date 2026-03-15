from os import environ
from typing import Callable, Mapping

import pytest
from dotenv import load_dotenv
from rich.console import Console
load_dotenv()
# environ.setdefault('OVERWRITE_PICKLE', 'True')  # Set PICKLED=True to override this
environ['INVOKED_BY_PYTEST'] = 'True'

from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.other_file import OtherFile
from epstein_files.documents.email import Email
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.output.rich import console as rich_console
from epstein_files.util.helpers.file_helper import *

FIXTURES_DIR = Path(__file__).parent.joinpath('fixtures', 'generated')
FILE_INFO_CSV_PATH = FIXTURES_DIR.joinpath('files.csv')
FILE_TEXT_DUMP_DIR = Path('source_data/processed')


@pytest.fixture
def doj_file_id() -> str:
    return 'EFTA02725909'  # memo to NYDFS for NYC bitcoin exchange


@pytest.fixture
def doj_filename(doj_file_id) -> str:
    return f"{doj_file_id}.txt"


@pytest.fixture
def doj_local_file_id(doj_file_id) -> str:
    return doj_file_id + '_28'


@pytest.fixture(scope='session')
def epstein_files() -> EpsteinFiles:
    return EpsteinFiles.get_files()


@pytest.fixture
def house_file_id_int() -> int:
    return 12345


@pytest.fixture
def house_file_id(house_file_id_int) -> str:
    return f"0{house_file_id_int}"


@pytest.fixture
def house_file_stem(house_file_id) -> str:
    return file_stem_for_id(house_file_id)


@pytest.fixture
def house_filename(house_file_stem) -> str:
    return f"{house_file_stem}.txt"


@pytest.fixture
def get_doj_file(epstein_files) -> Callable[[str], DojFile]:
    def _get_doj_file(id: str):
        return epstein_files.get_id(id, required_type=DojFile)

    return _get_doj_file


@pytest.fixture
def get_email(epstein_files) -> Callable[[str], Email]:
    def _get_email(id: str):
        return epstein_files.get_id(id, required_type=Email)

    return _get_email


@pytest.fixture
def get_other_file(epstein_files) -> Callable[[str], OtherFile]:
    def _get_other_file(id: str):
        return epstein_files.get_id(id, required_type=OtherFile)

    return _get_other_file


@pytest.fixture
def house_extract_file_id(house_file_id) -> str:
    return f"{house_file_id}_1"


@pytest.fixture
def house_extract_filename(house_extract_file_id) -> str:
    return f"{HOUSE_OVERSIGHT_PREFIX}{house_extract_file_id}.txt"


# Just for convenience
@pytest.fixture
def console() -> Console:
    return rich_console


def assert_higher_counts(actual: Mapping[str | None, int], expected: Mapping[str | None, int]):
    for key, count in actual.items():
        assert key in expected, f"{key} with {count} is in actual results but not in expected"
        assert count >= expected[key], f"Expected {expected[key]} for {key}, found {count}"
