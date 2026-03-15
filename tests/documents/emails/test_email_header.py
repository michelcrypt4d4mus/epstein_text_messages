from epstein_files.documents.email import Email
from epstein_files.documents.emails.email_header import EmailHeader

EMPTY_HEADER = """
From:
Sent:
To:
Subject:"""

NON_EMPTY_HEADER = """
From: Nas
Sent:
To:
Subject: Illmatic"""


def test_is_empty():
    assert EmailHeader(field_names=[]).is_empty
    assert EmailHeader.from_header_lines(EMPTY_HEADER).is_empty
    assert not EmailHeader.from_header_lines(NON_EMPTY_HEADER).is_empty


def test_is_to_redacted(get_email, console):
    assert get_email('030889').header.is_to_redacted is False
    assert get_email('EFTA02230132').header.is_to_redacted is True
