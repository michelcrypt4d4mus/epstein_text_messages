from epstein_files.documents.emails.emailers import cleanup_str, extract_emailer_names

USANYS_FROM = ' " < >, \' (USANYS)" '


def test_extract_emailer_names():
    assert extract_emailer_names('Edward Epstein') == ['Edward Jay Epstein']
    assert cleanup_str(USANYS_FROM)
    assert extract_emailer_names(USANYS_FROM) == ['USANYS']
