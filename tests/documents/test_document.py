

def test_is_doj_file(doj_file, messenger_log):
    assert doj_file.is_doj_file is True
    assert messenger_log.is_doj_file is False
