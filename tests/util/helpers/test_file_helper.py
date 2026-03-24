from epstein_files.documents.email import Email
from epstein_files.util.helpers.file_helper import *

DOJ_ID = 'EFTA01001153'


def test_build_filename_for_id():
    assert file_stem_for_id(123) == 'HOUSE_OVERSIGHT_000123'
    assert file_stem_for_id('001234_2') == 'HOUSE_OVERSIGHT_001234_2'


def test_coerce_file_stem(house_file_id, house_file_stem, house_filename, house_extract_filename):
    assert coerce_file_stem(house_file_id) == house_file_stem
    assert coerce_file_stem(house_file_stem) == house_file_stem
    assert coerce_file_stem(house_filename) == house_file_stem
    assert coerce_file_stem(house_extract_filename) == 'HOUSE_OVERSIGHT_012345_1'


def test_coerce_url_slug(doj_file_id, doj_filename, doj_local_file_id, house_filename, house_extract_filename):
    assert coerce_url_slug(doj_file_id) == doj_file_id
    assert coerce_url_slug(doj_filename) == doj_file_id
    assert coerce_url_slug(doj_local_file_id) == doj_file_id


def test_extract_file_id(doj_file_id, doj_filename, house_file_id, house_filename, house_extract_file_id, house_extract_filename):
    assert extract_file_id(house_filename) == house_file_id
    assert extract_file_id(house_extract_filename) == house_extract_file_id
    assert extract_file_id(doj_file_id) == doj_file_id
    assert extract_file_id(doj_filename) == doj_file_id
    assert extract_file_id('EFTA01880902EFTA02507454') == 'wfwew'


def test_is_local_file_extract(doj_file_id, doj_filename, house_filename, house_extract_filename):
    assert is_local_extract_file(house_extract_filename) is True
    assert is_local_extract_file(house_filename) is False
    assert is_local_extract_file(f'{doj_file_id}_1.txt') is True
    assert is_local_extract_file(doj_filename) is False


def test_is_valid_id(doj_local_file_id, house_extract_file_id, house_file_id):
    assert is_valid_id(DOJ_ID)
    assert is_valid_id(doj_local_file_id)
    assert is_valid_id(house_file_id)
    assert is_valid_id(house_extract_file_id)
    assert not is_valid_id(f"{DOJ_ID}{DOJ_ID}")


def test_local_doj_file_path(get_email):
    email: Email = get_email(DOJ_ID)
    assert email.file_info.local_pdf_path == local_doj_file_path(DOJ_ID, 9)
