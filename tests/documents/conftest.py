import pytest

from epstein_files.documents.document import Document
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.messenger_log import MessengerLog

DOJ_FILE_ID = 'EFTA00005783'
MESSENGER_LOG_ID = '027133'


@pytest.fixture
def doj_file() -> DojFile:
    return DojFile.from_file_id(DOJ_FILE_ID)


@pytest.fixture
def messenger_log() -> MessengerLog:
    return MessengerLog.from_file_id(MESSENGER_LOG_ID)
