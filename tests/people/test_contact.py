from rich.text import Text

from epstein_files.documents.emails.emailers import CONTACTS_DICT
from epstein_files.people.contact import Contact, acronym, organization, epstein_co, epstein_trust
from epstein_files.people.names import *

NAME = 'Nasir Jones'
EMAILER_PATTERN = r"Nasir[-_.\s]*Jones?"
HIGHLIGHT_PATTERN = fr"{EMAILER_PATTERN}|Jones,?[-_.\s]*Nasir"
URL = 'https://nasir.jones/ill'
WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/Nasir_Jones'

CONTACT_INFO = Contact(
    name=JEFFREY_EPSTEIN,
    emailer_pattern=r"Jeffrey Epstein|jeevacation",
    info="one and only"
)


def test_acronym():
    ipi = acronym(INTERNATIONAL_PEACE_INSTITUTE)
    assert ipi.name == 'IPI'
    assert ipi.info == INTERNATIONAL_PEACE_INSTITUTE
    assert ipi.emailer_pattern == r"I\.?P\.?I\.?|International Peace Institute"
    ipi = acronym(INTERNATIONAL_PEACE_INSTITUTE, 'Terje org')
    assert ipi.info == f"{INTERNATIONAL_PEACE_INSTITUTE}, Terje org"
    ofac = acronym('Office of Foreign Assets Control')
    assert ofac.name == 'OFAC'
    assert ofac.emailer_pattern == r"O\.?F\.?A\.?C\.?|Office of Foreign Assets Control"
    occ = acronym('Office of the Comptroller of the Currency')
    assert occ.name == 'OCC'


def test_bio():
    yulia = CONTACTS_DICT[YULIA_DOROKHINA]


def test_epstein_co():
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
    def assert_highlight_pattern_suffix(c: Contact, suffix: str):
        assert c.emailer_regex.pattern == EMAILER_PATTERN
        assert c.highlight_pattern == fr"{HIGHLIGHT_PATTERN}|{suffix}"

    assert_highlight_pattern_suffix(_build_contact(), 'Jones')
    assert_highlight_pattern_suffix(_build_contact(match_partial='both'), 'Nasir|Jones')
    assert_highlight_pattern_suffix(_build_contact(match_partial='first'), 'Nasir')

    jean_luc = Contact(JEAN_LUC_BRUNEL, match_partial='both')
    assert jean_luc.highlight_pattern == r'Jean[-_.\s]*Luc[-_.\s]*Brunel?|Brunel,?[-_.\s]*Jean[-_.\s]*Luc|Jean[-_.\s]*Luc|Brunel'


def test_middle_initial():
    assert CONTACT_INFO._middle_initial == ''
    assert Contact('Robert Dow Critton')._middle_initial == ''
    assert Contact('Robert D Critton')._middle_initial == 'D'
    critton = Contact('Robert D. Critton')
    assert critton._middle_initial == 'D'
    assert critton.emailer_regex.pattern == r"Robert[-_.\s]*(D\.?[-_.\s]*)?Critton?"


def test_organization():
    assert organization('Jege LLC').emailer_pattern == r"Jege(,? LLC)?"
    assert organization('Jege, LLC').emailer_pattern == r"Jege(,? LLC)?"
    assert organization('Butterfly Inc').emailer_pattern == r"Butterfly(,? Inc)?"
    assert organization('Butterfly, Inc.').emailer_pattern == r"Butterfly(,? Inc\.?)?"
    coatue = organization('Coatue Management', 'VC fund')
    assert coatue.emailer_pattern == r'Coatue( Management)?'


def test_pattern():
    assert _build_contact().pattern == EMAILER_PATTERN
    assert Contact('Robert D Critton').pattern == r"Robert[-_.\s]*(D\.?[-_.\s]*)?Critton?"


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


def test_urls():
    c = Contact('Nasir Jones', url='WIKIPEDIA')
    assert c.links[0].url == WIKIPEDIA_URL
    c = Contact('Nasir Jones', url=['WIKIPEDIA', URL])
    assert c.links[0].url == WIKIPEDIA_URL
    c = Contact('Nasir Jones', url=[URL, 'WIKIPEDIA'])
    assert c.name_link == Text.from_markup(f'[link={URL}][bold underline]Nasir Jones[/bold underline][/link]')


def _build_contact(**kwargs) -> Contact:
    return Contact(NAME, **kwargs)
