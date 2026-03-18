import pytest

from epstein_files.documents.email import JUNK_EMAILERS, Email
from epstein_files.people.names import *


@pytest.fixture
def attributed_email(get_email) -> Email:
    return get_email('033071')


@pytest.fixture
def article_with_fwd_text(get_email) -> Email:
    return get_email('016413')


@pytest.fixture
def non_article_with_fwd_text(get_email) -> Email:
    return get_email('012197_4')


def test_attached_docs(email_with_attachments):
    assert len(email_with_attachments.attached_docs) == 3


def test_author_and_border_style(attributed_email):
    assert attributed_email.author_style == 'blue1'
    assert attributed_email.border_style == 'blue1'
    assert attributed_email.recipient_style == 'purple'


def test_broken_header_repair(get_email):
    broken_email = get_email('032213')
    assert broken_email.actual_text == 'https://www.thedailybeast.com/how-close-is-donald-trump-to-a-psychiatric-breakdown?ref=home\n<...snipped jeffrey epstein email signature...>'
    assert broken_email.header.num_header_rows == 5


def test_extract_recipients(get_email):
    email_to_self: Email = get_email('EFTA01917209').reload()
    assert email_to_self.author == BROCK_PIERCE
    assert BROCK_PIERCE not in email_to_self.recipients


def test_info_sentences(get_email):
    email = get_email('026290')
    assert len(email.subheaders) == 1
    email_with_description = get_email('031278')
    assert len(email_with_description.subheaders) == 1
    assert email_with_description._config.note_txt is not None
    email: Email = get_email('EFTA00901581')
    assert email._config.note_txt is None
    svet = get_email('EFTA01870453')
    assert len(svet.subheaders) == 1
    assert svet.subheaders[0].plain == 'OCR text of email from Svetlana Pozhidaeva (???) to Jeffrey Epstein probably sent at 2011-04-05 16:51:26'
    assert svet._config.note_txt.plain == 'Svetlana Pozhidaeva fwds a discussion about an abortion to Epstein, see quote: "You have known you are preg for a week"'


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
