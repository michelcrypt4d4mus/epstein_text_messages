from epstein_files.people.contact import Contact
from epstein_files.util.constant.names import JEFFREY_EPSTEIN


CONTACT_INFO = Contact(
    name=JEFFREY_EPSTEIN,
    emailer_pattern=r"Jeffrey Epstein|jeevacation",
    info="one and only"
)


def test_repr():
    assert repr(CONTACT_INFO) == """Contact(
    name=JEFFREY_EPSTEIN,
    info="one and only",
    emailer_pattern=r"Jeffrey Epstein|jeevacation",
)"""
