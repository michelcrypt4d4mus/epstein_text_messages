from os import environ

import pytest
from dotenv import load_dotenv
load_dotenv()
environ.setdefault('OVERWRITE_PICKLE', 'True')  # Set PICKLED=True to override this
environ['INVOKED_BY_PYTEST'] = 'True'

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
def local_extract_file_name(file_stem) -> str:
    return f"{file_stem}_1.txt"
