from epstein_files.util.file_helper import *


def test_is_local_file_extract(local_extract_file_name):
    assert local_extract_file_name == 'HOUSE_OVERSIGHT_012345_1.txt'
    assert is_local_extract_file(local_extract_file_name) is True
