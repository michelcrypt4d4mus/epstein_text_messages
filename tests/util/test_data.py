from epstein_files.util.data import extract_last_name


def test_extract_last_name():
    assert extract_last_name("Thomas Landon") == "Landon"
    assert extract_last_name("Thomas Landon Jr.") == "Landon Jr."
