from epstein_files.people.contact import Contact, epstein_co, epstein_trust
from epstein_files.util.constant.names import JEFFREY_EPSTEIN

NAME = 'Nasir Jones'
EMAILER_PATTERN = r"Nasir[-_.\s]*Jones?"

CONTACT_INFO = Contact(
    name=JEFFREY_EPSTEIN,
    emailer_pattern=r"Jeffrey Epstein|jeevacation",
    info="one and only"
)


def test_repr():
    assert repr(CONTACT_INFO) == r"""Contact(
    name=JEFFREY_EPSTEIN,
    info="one and only",
    emailer_pattern=r"Jeffrey Epstein|jeevacation",
    is_emailer="True",
    is_interesting="True",
    match_partial_names="last",
    highlight_pattern=r"Jeffrey[-_.\s]*Epstein|jeevacation|Epstein,?[-_.\s]*Jeffrey|Epstein",
)"""


def test_epstein_co():
    jege = epstein_co('Jege LLC')
    assert jege.emailer_pattern == r"Jege( LLC)?"
    butterfly = epstein_co('Butterfly Inc')
    assert butterfly.emailer_pattern == r"Butterfly( Inc)?"
    butterfly = epstein_co('Butterfly, Inc.')
    assert butterfly.emailer_pattern == r"Butterfly(,? Inc\.?)?"


def test_epstein_trust():
    butterfly = epstein_trust('Butterfly Trust', beneficiaries=['Karyna'])
    assert butterfly.info == 'Epstein financial trust, sole beneficiary Karyna'
    butterfly = epstein_trust('Butterfly Trust', beneficiaries=['Karyna', 'Dave'])
    assert butterfly.info == "Epstein financial trust, beneficiaries Karyna, Dave"


def test_highlight_pattern():
    c = _build_contact()
    assert c.emailer_regex.pattern == EMAILER_PATTERN
    assert c.highlight_pattern == r"Nasir[-_.\s]*Jones?|Jones,?[-_.\s]*Nasir|Jones"
    c = _build_contact(match_partial_names='both')
    assert c.emailer_regex.pattern == EMAILER_PATTERN
    assert c.highlight_pattern == r"Nasir[-_.\s]*Jones?|Jones,?[-_.\s]*Nasir|Nasir|Jones"
    c = _build_contact(match_partial_names='first')
    assert c.emailer_regex.pattern == EMAILER_PATTERN
    assert c.highlight_pattern == r"Nasir[-_.\s]*Jones?|Jones,?[-_.\s]*Nasir|Nasir"


def _build_contact(**kwargs) -> Contact:
    return Contact(NAME, **kwargs)
