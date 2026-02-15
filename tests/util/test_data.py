from epstein_files.util.constant.names import extract_last_name
from epstein_files.util.helpers.data_helpers import constantize_names


def test_constantize_names():
    assert constantize_names(f"Jeffrey Epstein's assistant Lesley Groff office") == "{JEFFREY_EPSTEIN}'s assistant {LESLEY_GROFF} office"


def test_extract_last_name():
    assert extract_last_name("Thomas") == "Thomas"
    assert extract_last_name("Thomas Landon") == "Landon"
    assert extract_last_name("Thomas Landon Jr.") == "Landon Jr."
