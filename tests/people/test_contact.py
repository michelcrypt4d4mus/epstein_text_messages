from epstein_files.people.contact import Contact, organization, epstein_co, epstein_trust
from epstein_files.util.constant.names import JEAN_LUC_BRUNEL, JEFFREY_EPSTEIN

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
    match_partial="last",
    highlight_pattern=r"Jeffrey[-_.\s]*Epstein|jeevacation|Epstein,?[-_.\s]*Jeffrey|Epstein",
)"""


def test_company():
    coatue = organization('Coatue Management', 'VC fund')
    assert coatue.emailer_pattern == r'Coatue( Management)?'


def test_epstein_co():
    jege = epstein_co('Jege LLC')
    assert jege.emailer_pattern == r"Jege( LLC)?"
    butterfly = epstein_co('Butterfly Inc')
    assert butterfly.emailer_pattern == r"Butterfly( Inc)?"
    butterfly = epstein_co('Butterfly, Inc.')
    assert butterfly.emailer_pattern == r"Butterfly(,? Inc\.?)?"
    zorro = epstein_co('Zorro', description='for New Mexico ranch')
    assert zorro.info == f"Epstein company for New Mexico ranch"


def test_epstein_trust():
    butterfly = epstein_trust('Butterfly Trust', beneficiaries=['Karyna'])
    assert butterfly.info == 'Epstein financial trust, sole beneficiary Karyna'
    butterfly = epstein_trust('Butterfly Trust', beneficiaries=['Karyna', 'Dave'])
    assert butterfly.info == "Epstein financial trust, beneficiaries Karyna, Dave"
    year_trust = epstein_trust('2012', trustees=['Bob', 'Dylan'])
    assert year_trust.name == 'Jeffrey E. Epstein 2012 Trust'
    assert year_trust.info == 'Epstein financial trust, trustees: Bob, Dylan'
    year_trust = epstein_trust('2012', trustees=['Bob', 'Dylan'], beneficiaries=['Karyna'])
    assert year_trust.info == 'Epstein financial trust, sole beneficiary Karyna, trustees: Bob, Dylan'


def test_highlight_pattern():
    c = _build_contact()
    assert c.emailer_regex.pattern == EMAILER_PATTERN
    assert c.highlight_pattern == r"Nasir[-_.\s]*Jones?|Jones,?[-_.\s]*Nasir|Jones"
    c = _build_contact(match_partial='both')
    assert c.emailer_regex.pattern == EMAILER_PATTERN
    assert c.highlight_pattern == r"Nasir[-_.\s]*Jones?|Jones,?[-_.\s]*Nasir|Nasir|Jones"
    c = _build_contact(match_partial='first')
    assert c.emailer_regex.pattern == EMAILER_PATTERN
    assert c.highlight_pattern == r"Nasir[-_.\s]*Jones?|Jones,?[-_.\s]*Nasir|Nasir"

    jean_luc = Contact(JEAN_LUC_BRUNEL, match_partial='both')
    assert jean_luc.highlight_pattern == r'Jean[-_.\s]*Luc[-_.\s]*Brunel?|Brunel,?[-_.\s]*Jean[-_.\s]*Luc|Jean[-_.\s]*Luc|Brunel'


def _build_contact(**kwargs) -> Contact:
    return Contact(NAME, **kwargs)
