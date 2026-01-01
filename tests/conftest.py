from dotenv import load_dotenv
load_dotenv()
import pytest

from epstein_files.epstein_files import EpsteinFiles
from epstein_files.util.file_helper import *


@pytest.fixture(scope='session')
def epstein_files() -> EpsteinFiles:
    return EpsteinFiles.get_files()


@pytest.fixture
def file_stem() -> str:
    return build_file_stem_for_id(12345)


@pytest.fixture
def file_name(file_stem) -> str:
    return f"{file_stem}.txt"


@pytest.fixture
def local_extract_file_name(file_stem) -> str:
    return f"{file_stem}_1.txt"
