import pytest

from epstein_files.documents.document import Document
from epstein_files.documents.documents.doc_cfg import DocCfg
from epstein_files.documents.doj_file import DojFile
from epstein_files.documents.email import Email
from epstein_files.documents.messenger_log import MessengerLog
from epstein_files.documents.other_file import OtherFile

DOJ_FILE_ID = 'EFTA00005783'
MESSENGER_LOG_ID = '027133'



@pytest.fixture
def harvard_poetry_doc(epstein_files) -> OtherFile:
    return epstein_files.get_id('023452', required_type=OtherFile)


@pytest.fixture
def harvard_poetry_cfg(harvard_poetry_doc) -> DocCfg:
    return harvard_poetry_doc.config


@pytest.fixture
def email() -> Email:
    return Email.from_file_id('019446')


@pytest.fixture
def messenger_log() -> MessengerLog:
    return MessengerLog.from_file_id(MESSENGER_LOG_ID)


@pytest.fixture
def other_file() -> OtherFile:
    return OtherFile.from_file_id('019448') # Jacmel Haiti proposal


# DOJ files
@pytest.fixture
def doj_file() -> DojFile:
    return DojFile.from_file_id(DOJ_FILE_ID)


@pytest.fixture
def doj_email_file() -> DojFile:
    return DojFile.from_file_id('EFTA00039689')


@pytest.fixture
def blockchain_capital_coinbase_nda(epstein_files) -> DojFile:
    return epstein_files.get_id('EFTA01082451', required_type=DojFile)


@pytest.fixture
def valar_ventures_doc(epstein_files) -> DojFile:
    return epstein_files.get_id('EFTA00609489', required_type=DojFile)
