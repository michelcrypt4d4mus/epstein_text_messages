from dotenv import load_dotenv
load_dotenv()
import pytest

from epstein_files.epstein_files import EpsteinFiles


@pytest.fixture(scope='session', autouse=True)
def epstein_files() -> EpsteinFiles:
    return EpsteinFiles.get_files()
