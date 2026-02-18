from os import environ
from typing import Callable, Mapping

import pytest
from dotenv import load_dotenv
load_dotenv()
# environ.setdefault('OVERWRITE_PICKLE', 'True')  # Set PICKLED=True to override this
environ['INVOKED_BY_PYTEST'] = 'True'

from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.other_file import OtherFile
from epstein_files.documents.email import Email
from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.helpers.file_helper import *


@pytest.fixture(scope='session')
def epstein_files() -> EpsteinFiles:
    return EpsteinFiles.get_files()


@pytest.fixture
def file_id() -> int:
    return 12345


@pytest.fixture
def file_stem(file_id) -> str:
    return file_stem_for_id(file_id)


@pytest.fixture
def file_name(file_stem) -> str:
    return f"{file_stem}.txt"


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
def local_extract_file_name(file_stem) -> str:
    return f"{file_stem}_1.txt"


def assert_higher_counts(actual: Mapping[str | None, int], expected: Mapping[str | None, int]):
    for key, count in actual.items():
        assert key in expected
        assert count >= expected[key], f"Expected {expected[key]} for {key}, found {count}"
