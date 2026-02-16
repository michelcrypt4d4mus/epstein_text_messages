from epstein_files.documents.email import JUNK_EMAILERS, Email


def test_border_style(get_email):
    email = get_email('033071')
    assert email.border_style == 'purple'
    assert email.author_style == 'blue1'


def test_broken_header_repair(get_email):
    broken_email = get_email('032213')
    assert broken_email.actual_text == 'https://www.thedailybeast.com/how-close-is-donald-trump-to-a-psychiatric-breakdown?ref=home\n<...snipped jeffrey epstein email signature...>'
    assert broken_email.header.num_header_rows == 5


def test_info_sentences(get_email):
    email = get_email('026290')
    assert len(email.info) == 1
    email_with_description = get_email('031278')
    assert len(email_with_description.info) == 2


def test_interesting(get_email):
    email = get_email('025041')
    assert not email.config.is_of_interest
    assert not email.is_interesting


def test_is_fwded_article(get_email):
    fwded_article = get_email('033311')
    assert fwded_article.is_word_count_worthy is False
    non_article_with_fwd_text = get_email('012197_4')
    assert non_article_with_fwd_text.is_fwded_article is False
    assert non_article_with_fwd_text.is_word_count_worthy is True

    article_with_fwd_text = get_email('016413')
    assert article_with_fwd_text.is_fwded_article is True
    assert article_with_fwd_text.is_word_count_worthy is True


def test_junk_emailers():
    assert len(JUNK_EMAILERS) == 5
