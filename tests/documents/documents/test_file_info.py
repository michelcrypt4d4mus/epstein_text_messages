import pytest

from epstein_files.documents.documents.file_info import FileInfo
from epstein_files.util.helpers.file_helper import DOCS_DIR, DOJ_TXTS_20260130_DIR


@pytest.fixture
def oversight_file_location():
    return FileInfo(DOCS_DIR.joinpath('HOUSE_OVERSIGHT_019407.txt'))


@pytest.fixture
def extract_location():
    return FileInfo(DOCS_DIR.joinpath('HOUSE_OVERSIGHT_014797_1.txt'))


@pytest.fixture
def doj_file_location():
    return FileInfo(DOJ_TXTS_20260130_DIR.joinpath('DataSet 10', 'EFTA01751416.txt'))


def test_url_slug(extract_location):
    assert extract_location.file_id == '014797_1'
    assert extract_location.url_slug == 'HOUSE_OVERSIGHT_014797'


def test_external_url(doj_file_location, extract_location, oversight_file_location):
    assert doj_file_location.external_url == 'https://www.justice.gov/epstein/files/DataSet%2010/EFTA01751416.pdf'
    assert extract_location.external_url == 'https://epstein.media/files/house_oversight_014797'
    assert oversight_file_location.external_url == 'https://epstein.media/files/house_oversight_019407'
