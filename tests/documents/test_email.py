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


@pytest.fixture
def email_with_category_but_no_note(get_email) -> Email:
    return get_email('EFTA00738485')


@pytest.fixture
def svet_email(get_email) -> Email:
    return get_email('EFTA01870453')


@pytest.fixture
def uninteresting_email(get_email) -> Email:
    return get_email('EFTA00037454')


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


def test_subheaders(get_email):
    email = get_email('026290')
    assert len(email.subheaders) == 1
    email_with_description = get_email('031278')
    assert len(email_with_description.subheaders) == 1
    assert email_with_description._config.note_txt is not None


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


def test_note(email_with_category_but_no_note, svet_email, uninteresting_email):
    assert svet_email._config.note_txt(include_category=False).plain == \
        'Svetlana Pozhidaeva fwds intimate texts from Joshua Fink about an abortion to Epstein, see quote: "You have known you are preg for a week"'

    assert uninteresting_email._config.note_txt() is None
    assert len(uninteresting_email.subheaders) == 1
    assert len(email_with_category_but_no_note.subheaders) == 1
    assert email_with_category_but_no_note.subheaders[0].plain.startswith('[girls]')
    assert not email_with_category_but_no_note._body_as_table().columns[0].header


def test_subheader(get_email, svet_email):
    assert len(svet_email.subheaders) == 1

    assert svet_email.subheaders[0].plain == \
        '[girls] OCR text of email from Svetlana Pozhidaeva (???) to Jeffrey Epstein sent at 2011-04-05 16:51:26'
    assert get_email('EFTA02730468').subheaders[0].plain == \
        '[government] OCR text of email from USANYS to USANYS probably sent at 2019-07-11 08:25:00'


def test_timestamp(attributed_email):
    assert attributed_email.timestamp_without_seconds == '2018-01-15 15:17'
