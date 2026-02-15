import pytest

from epstein_files.documents.email import Email
from epstein_files.util.constant.names import *
from epstein_files.util.helpers.data_helpers import dict_sets_to_lists

from .fixtures.emails.email_author_counts import EMAIL_AUTHOR_COUNTS
from .fixtures.emails.email_recipient_counts import EMAIL_RECIPIENT_COUNTS
from .fixtures.emails.signatures import AUTHORS_TO_DEVICE_SIGNATURES, DEVICE_SIGNATURE_TO_AUTHORS, SIGNATURE_SUBSTITUTION_COUNTS
from .fixtures.emails.unknown_recipient_file_ids import UNKNOWN_RECIPIENT_FILE_IDS


@pytest.mark.skip(reason='temporary')
def test_email_author_counts(epstein_files):
    author_counts = epstein_files.email_author_counts()
    assert author_counts.pop(JEFFREY_EPSTEIN) > 790
    assert author_counts.pop(LESLEY_GROFF) > 100
    assert author_counts.pop(RICHARD_KAHN) > 50
    assert author_counts == EMAIL_AUTHOR_COUNTS


@pytest.mark.skip(reason='temporary')
def test_email_recipient_counts(epstein_files):
    recipient_counts = epstein_files.email_recipient_counts()
    assert recipient_counts.pop(JEFFREY_EPSTEIN) > 1800
    assert recipient_counts.pop(LESLEY_GROFF) > 40
    assert recipient_counts.pop(RICHARD_KAHN) > 50
    assert recipient_counts == EMAIL_RECIPIENT_COUNTS


def test_info_sentences(epstein_files):
    email = epstein_files.get_id('026290')
    assert len(email.info) == 1
    email_with_description = epstein_files.get_id('031278')
    assert len(email_with_description.info) == 2


def test_signatures(epstein_files):
    assert dict_sets_to_lists(epstein_files.email_authors_to_device_signatures()) == AUTHORS_TO_DEVICE_SIGNATURES
    assert dict_sets_to_lists(epstein_files.email_device_signatures_to_authors()) == DEVICE_SIGNATURE_TO_AUTHORS


def test_signature_substitutions(epstein_files):
    substitution_counts = epstein_files.email_signature_substitution_counts()
    # epstein_substitutions = substitution_counts.pop(JEFFREY_EPSTEIN)
    # assert epstein_substitutions > 3840
    assert substitution_counts == SIGNATURE_SUBSTITUTION_COUNTS


def test_unknown_recipient_file_ids(epstein_files):
    assert epstein_files.unknown_recipient_ids() == UNKNOWN_RECIPIENT_FILE_IDS


def test_border_style(epstein_files):
    email = epstein_files.get_id('033071', required_type=Email)
    assert email.border_style == 'purple'
    assert email.author_style == 'blue1'


def test_is_fwded_article(epstein_files):
    fwded_article = epstein_files.get_id('033311', required_type=Email)
    assert fwded_article.is_word_count_worthy is False
    non_article_with_fwd_text = epstein_files.get_id('012197_4', required_type=Email)
    assert non_article_with_fwd_text.is_fwded_article is False
    assert non_article_with_fwd_text.is_word_count_worthy is True
    article_with_fwd_text = epstein_files.get_id('016413', required_type=Email)
    assert article_with_fwd_text.is_fwded_article is True
    assert article_with_fwd_text.is_word_count_worthy is True


def test_broken_header_repair(epstein_files):
    broken_email = epstein_files.get_id('032213', required_type=Email)
    assert broken_email.actual_text == 'https://www.thedailybeast.com/how-close-is-donald-trump-to-a-psychiatric-breakdown?ref=home\n<...snipped jeffrey epstein email signature...>'
    assert broken_email.header.num_header_rows == 5
