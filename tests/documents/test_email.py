import pytest

from epstein_files.documents.email import JUNK_EMAILERS, Email


@pytest.fixture
def attributed_email(get_email) -> Email:
    return get_email('033071')


@pytest.fixture
def article_with_fwd_text(get_email) -> Email:
    return get_email('016413')


@pytest.fixture
def non_article_with_fwd_text(get_email) -> Email:
    return get_email('012197_4')


def test_attached_docs(get_email):
    email_with_attached: Email = get_email('029299')
    assert len(email_with_attached.attached_docs) == 3


def test_author_and_border_style(attributed_email):
    assert attributed_email.author_style == 'blue1'
    assert attributed_email.border_style == 'blue1'
    assert attributed_email.recipient_style == 'purple'


def test_broken_header_repair(get_email):
    broken_email = get_email('032213')
    assert broken_email.actual_text == 'https://www.thedailybeast.com/how-close-is-donald-trump-to-a-psychiatric-breakdown?ref=home\n<...snipped jeffrey epstein email signature...>'
    assert broken_email.header.num_header_rows == 5


def test_info_sentences(get_email):
    email = get_email('026290')
    assert len(email.info) == 1
    email_with_description = get_email('031278')
    assert len(email_with_description.info) == 1


def test_is_interesting(get_email, ito_email):
    assert ito_email.is_interesting
    email = get_email('025041')
    assert not email.config.is_of_interest
    assert not email.is_interesting


def test_is_fwded_article(article_with_fwd_text, get_email, non_article_with_fwd_text):
    assert get_email('EFTA02334332').is_word_count_worthy is True
    fwded_article = get_email('033311')
    assert fwded_article.is_word_count_worthy is False
    assert non_article_with_fwd_text.is_fwded_article is False
    assert article_with_fwd_text.is_fwded_article is True


@pytest.mark.skip('fwded_text_after is wonky')
def test_is_word_count_worthy_fwded_text_after(article_with_fwd_text, non_article_with_fwd_text):
    assert non_article_with_fwd_text.is_word_count_worthy is True
    assert article_with_fwd_text.is_word_count_worthy is True


def test_junk_emailers():
    assert len(JUNK_EMAILERS) == 5


def test_timestamp(attributed_email):
    assert attributed_email.timestamp_without_seconds == '2018-01-15 15:17'
