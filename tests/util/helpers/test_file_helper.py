from epstein_files.util.helpers.file_helper import *


def test_build_filename_for_id():
    assert file_stem_for_id(123) == 'HOUSE_OVERSIGHT_000123'
    assert file_stem_for_id('001234_2') == 'HOUSE_OVERSIGHT_001234_2'


def test_is_local_file_extract(doj_file_id, doj_filename, house_filename, local_extract_file_name):
    assert is_local_extract_file(local_extract_file_name) is True
    assert is_local_extract_file(house_filename) is False
    assert is_local_extract_file(f'{doj_file_id}_1.txt') is True
    assert is_local_extract_file(doj_filename) is False


def test_coerce_file_stem(house_file_id, house_file_stem, house_filename, local_extract_file_name):
    assert coerce_file_stem(house_file_id) == house_file_stem
    assert coerce_file_stem(house_file_stem) == house_file_stem
    assert coerce_file_stem(house_filename) == house_file_stem
    assert coerce_file_stem(local_extract_file_name) == 'HOUSE_OVERSIGHT_012345_1'
