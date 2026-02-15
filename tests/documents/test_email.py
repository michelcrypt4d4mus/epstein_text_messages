
from epstein_files.documents.email import JUNK_EMAILERS, Email


def test_border_style(epstein_files):
    email = epstein_files.get_id('033071', required_type=Email)
    assert email.border_style == 'purple'
    assert email.author_style == 'blue1'


def test_broken_header_repair(epstein_files):
    broken_email = epstein_files.get_id('032213', required_type=Email)
    assert broken_email.actual_text == 'https://www.thedailybeast.com/how-close-is-donald-trump-to-a-psychiatric-breakdown?ref=home\n<...snipped jeffrey epstein email signature...>'
    assert broken_email.header.num_header_rows == 5


def test_info_sentences(epstein_files):
    email = epstein_files.get_id('026290')
    assert len(email.info) == 1
    email_with_description = epstein_files.get_id('031278')
    assert len(email_with_description.info) == 2


def test_interesting(epstein_files):
    email = epstein_files.get_id('025041', required_type=Email)
    assert not email.config.is_of_interest
    assert not email.is_interesting


def test_junk_emailers():
    assert len(JUNK_EMAILERS) == 5


def test_is_fwded_article(epstein_files):
    fwded_article = epstein_files.get_id('033311', required_type=Email)
    assert fwded_article.is_word_count_worthy is False
    non_article_with_fwd_text = epstein_files.get_id('012197_4', required_type=Email)
    assert non_article_with_fwd_text.is_fwded_article is False
    assert non_article_with_fwd_text.is_word_count_worthy is True
    article_with_fwd_text = epstein_files.get_id('016413', required_type=Email)
    assert article_with_fwd_text.is_fwded_article is True
    assert article_with_fwd_text.is_word_count_worthy is True
