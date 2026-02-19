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
