
from epstein_files.documents.email import JUNK_EMAILERS, Email


def test_junk_emailers():
    assert len(JUNK_EMAILERS) == 5


def test_interesting(epstein_files):
    email = epstein_files.get_id('025041', required_type=Email)
    assert not email.config.is_of_interest
    assert not email.is_interesting
