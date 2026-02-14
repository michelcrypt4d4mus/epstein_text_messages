from epstein_files.documents.emails.emailers import extract_emailer_names


def test_extract_emailer_names():
    assert extract_emailer_names('Edward Epstein') == ['Edward Jay Epstein']
