from os import devnull

from dotenv import load_dotenv
load_dotenv()
from rich.console import Console
import pytest

from epstein_files.epstein_files import EpsteinFiles


@pytest.fixture(scope='session', autouse=True)
def epstein_files() -> EpsteinFiles:
    epstein_files = EpsteinFiles()

    # sender_counts are only built when printed :(
    with open(devnull, "wt") as null_out:
        console = Console(file=null_out)

        for doc in (epstein_files.imessage_logs + epstein_files.emails):
            console.print(doc)

    return epstein_files
