from epstein_files.util.data import extract_datetime


def test_extract_datetime():
    s = f"article about Venice Film Festival 2011-09-06"
    d = extract_datetime(s)
    assert d is not None
    assert d.isoformat() == '2011-09-06T00:00:00'

    s = f"draft about Oscars in 2011-02 (?)"
    d = extract_datetime(s)
    assert d is not None
    assert d.isoformat() == '2011-02-01T00:00:00'
