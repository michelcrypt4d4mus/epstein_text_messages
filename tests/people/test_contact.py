from epstein_files.people.contact import Contact, epstein_co
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


def test_epstein_co():
    jege = epstein_co('Jege LLC')
    assert jege.emailer_pattern == r"Jege( LLC)?"
    butterfly = epstein_co('Butterfly Inc')
    assert butterfly.emailer_pattern == r"Butterfly( Inc)?"
    butterfly = epstein_co('Butterfly Inc.')
    assert butterfly.emailer_pattern == r"Butterfly( Inc\.?)?"
