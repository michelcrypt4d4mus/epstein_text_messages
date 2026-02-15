from epstein_files.util.helpers.file_helper import *


def test_build_filename_for_id():
    assert file_stem_for_id(123) == 'HOUSE_OVERSIGHT_000123'
    assert file_stem_for_id('001234_2') == 'HOUSE_OVERSIGHT_001234_2'


def test_is_local_file_extract(local_extract_file_name):
    assert local_extract_file_name == 'HOUSE_OVERSIGHT_012345_1.txt'
    assert is_local_extract_file(local_extract_file_name) is True


def test_coerce_file_stem(file_id, file_stem, file_name, local_extract_file_name):
    assert coerce_file_stem(file_id) == file_stem
    assert coerce_file_stem(file_stem) == file_stem
    assert coerce_file_stem(file_name) == file_stem
    assert coerce_file_stem(local_extract_file_name) == 'HOUSE_OVERSIGHT_012345_1'
