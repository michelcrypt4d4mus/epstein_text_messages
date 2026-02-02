import pytest

from epstein_files.documents.document import Document
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile

DOJ_FILE_ID = 'EFTA00005783'
MESSENGER_LOG_ID = '027133'


@pytest.fixture
def doj_file() -> DojFile:
    return DojFile.from_file_id(DOJ_FILE_ID)


@pytest.fixture
def doj_file_thats_an_email() -> DojFile:
    return DojFile.from_file_id('EFTA00039689')


@pytest.fixture
def email() -> Email:
    return Email.from_file_id('019446')


@pytest.fixture
def messenger_log() -> MessengerLog:
    return MessengerLog.from_file_id(MESSENGER_LOG_ID)


@pytest.fixture
def other_file() -> OtherFile:
    return OtherFile.from_file_id('019448') # Jacmel Haiti proposal
