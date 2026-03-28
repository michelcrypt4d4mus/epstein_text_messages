from copy import deepcopy

import pytest
from rich.text import Text

from epstein_files.documents.emails.emailers import ENTITIES_DICT
from epstein_files.people.entity import Entity, Organization, acronym, epstein_co, epstein_trust, law_enforcement
from epstein_files.people.names import *
from epstein_files.util.constant.strings import WIKIPEDIA

NAME = 'Nasir Jones'
EMAILER_PATTERN = r"Nasir[-_.\s]*Jones?|Jones,?[-_.\s]*Nasir?"
HIGHLIGHT_PATTERN = fr"{EMAILER_PATTERN}|Jones,?[-_.\s]*Nasir"
URL = 'https://nasir.jones/ill'
WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/Nasir_Jones'


@pytest.fixture
def epstein() -> Entity:
    return Entity(
        name=JEFFREY_EPSTEIN,
        emailer_pattern=r"Jeffrey Epstein|jeevacation",
        info="one and only"
    )


def test_acronym():
    ipi = acronym(INTERNATIONAL_PEACE_INSTITUTE)
    assert ipi.name == 'IPI'
    assert ipi.info == INTERNATIONAL_PEACE_INSTITUTE
    assert ipi.emailer_pattern == r"I\.?P\.?I\.?|International Peace Institute"
    assert ipi.is_emailer is False
    ipi = acronym(INTERNATIONAL_PEACE_INSTITUTE, 'Terje org')
    assert ipi.info == f"{INTERNATIONAL_PEACE_INSTITUTE}, Terje org"
    ofac = acronym('Office of Foreign Assets Control')
    assert ofac.name == 'OFAC'
    assert ofac.emailer_pattern == r"O\.?F\.?A\.?C\.?|Office of Foreign Assets Control"
    occ = acronym('Office of the Comptroller of the Currency')
    assert occ.name == 'OCC'
    dbagny = acronym("Deutsche Bank AG New York")
    assert dbagny.name == 'DBAGNY'


def test_bio():
    yulia = ENTITIES_DICT[YULIA_DOROKHINA]
    brock = ENTITIES_DICT[BROCK_PIERCE]

    assert brock.bio_txt.plain == \
        'Brock Pierce [crypto] sex crime history, Bannon partner at IGN, Tether co-founder, friend of Yair Netanyahu [protos/cryptadamus/wiki]'


def test_epstein_co():
    zorro = epstein_co('Zorro', info='for New Mexico ranch')
    assert zorro.info == f"Epstein company for New Mexico ranch"


def test_epstein_site_links(epstein):
    assert epstein.epstein_site_link().url == 'https://epsteinify.com/?name=Jeffrey%20Epstein'
    assert epstein.epstein_sites_all_links.plain == 'Carstensen / epstein.media / EpsteinWeb / epsteinify / Jmail / search X'


def test_epstein_trust():
    butterfly = epstein_trust(BUTTERFLY_TRUST, beneficiaries=['Karyna'])
    assert butterfly.info == 'Epstein financial trust, sole beneficiary Karyna'
    assert butterfly.match_partial == 'suffix'
    butterfly = epstein_trust(BUTTERFLY_TRUST, beneficiaries=['Karyna', 'Dave'])
    assert butterfly.info == "Epstein financial trust, beneficiaries Karyna, Dave"
    year_trust = epstein_trust('2012', trustees=['Bob', 'Dylan'])
    assert year_trust.name == 'Jeffrey E. Epstein 2012 Trust'
    assert year_trust.info == 'Epstein financial trust, trustees: Bob, Dylan'
    year_trust = epstein_trust('2012', trustees=['Bob', 'Dylan'], beneficiaries=['Karyna'])
    assert year_trust.info == 'Epstein financial trust, sole beneficiary Karyna, trustees: Bob, Dylan'


def test_highlight_pattern():
    def assert_highlight_pattern_suffix(c: Entity, suffix: str):
        assert c.emailer_regex.pattern == EMAILER_PATTERN
        assert c.highlight_pattern == fr"{HIGHLIGHT_PATTERN}|{suffix}"

    assert_highlight_pattern_suffix(_build_contact(), 'Jones')
    assert_highlight_pattern_suffix(_build_contact(match_partial='both'), 'Nasir|Jones')
    assert_highlight_pattern_suffix(_build_contact(match_partial='first'), 'Nasir')

    jean_luc = Entity(JEAN_LUC_BRUNEL, match_partial='both')
    assert jean_luc.highlight_pattern == r'Jean[-_.\s]*Luc[-_.\s]*Brunel?|Brunel,?[-_.\s]*Jean[-_.\s]*Luc|Jean[-_.\s]*Luc|Brunel'


def test_law_enforcment():
    usao = law_enforcement('US Attorney')
    assert usao.is_emailer is False
    assert usao.highlight_regex.pattern == r'\b(U(\.|nited)?[-_.\s]*S(\.|tates)?[-_.\s]*Attorney)\b'
    assert usao.highlight_regex.match('US Attorney')
    assert usao.highlight_regex.match('U.S. Attorney')
    assert usao.highlight_regex.match('United States Attorney')


def test_links():
    naomi = ENTITIES_DICT[NAOMI_CAMPBELL]
    assert 'wiki' in naomi.links_txt().plain
    assert 'wiki' not in naomi.links_txt(False).plain


def test_middle_initial(epstein):
    assert epstein._middle_initial == ''
    assert Entity('Robert Dow Critton')._middle_initial == ''
    assert Entity('Robert D Critton')._middle_initial == 'D'
    critton = Entity('Robert D. Critton')
    assert critton._middle_initial == 'D'
    assert critton.emailer_regex.pattern == r"Robert[-_.\s]*(D\.?[-_.\s]*)?Critton?|Critton,?[-_.\s]*Robert?"


def test_organization():
    jege = Organization('Jege LLC')
    assert jege.emailer_pattern == r"Jege(,? LLC)?"
    assert jege.match_partial == 'suffix'
    assert jege.is_emailer is None
    assert Organization('Jege, LLC').emailer_pattern == r"Jege(,? LLC)?"
    assert Organization('Jege, LLC', match_partial=None).emailer_pattern == ''
    assert Organization('Butterfly Inc').emailer_pattern == r"Butterfly(,? Inc)?"
    assert Organization('Butterfly, Inc.').emailer_pattern == r"Butterfly(,? Inc\.?)?"
    assert Organization(USANYS).emailer_regex.pattern == 'USANYS'
    coatue = Organization('Coatue Management', 'VC fund')
    assert coatue.match_partial == 'suffix'
    assert coatue.emailer_pattern == r'Coatue( Management)?'
    northward = Organization('NorthwardEducation')
    assert northward.emailer_regex.pattern == 'NorthwardEducation'
    thielcap = Organization('ThielCapital', belongs_to=PETER_THIEL)
    assert thielcap.info == f"{PETER_THIEL} organization"


def test_pattern():
    assert _build_contact().pattern == EMAILER_PATTERN
    assert Entity('Robert D Critton').pattern == r"Robert[-_.\s]*(D\.?[-_.\s]*)?Critton?|Critton,?[-_.\s]*Robert?"
    assert Entity('Alan J. Dlugash').pattern == r"Alan[-_.\s]*(J\.?[-_.\s]*)?Dlugash?|Dlugash,?[-_.\s]*Alan?"


def test_repr(epstein):
    jee = deepcopy(epstein)
    jee.style = 'bright_red'
    assert repr(jee) == r"""Entity(
    name=JEFFREY_EPSTEIN,
    info="one and only",
    emailer_pattern=r"Jeffrey Epstein|jeevacation",
    is_emailer="True",
    is_interesting="True",
    is_scannable="True",
    match_partial="last",
    style="bright_red",
    highlight_pattern=r"Jeffrey[-_.\s]*Epstein|jeevacation|Epstein,?[-_.\s]*Jeffrey|Epstein",
)"""


def test_urls():
    c = Entity('Nasir Jones', url=WIKIPEDIA)
    assert c._urls[0] == WIKIPEDIA_URL
    c = Entity('Nasir Jones', url=[WIKIPEDIA, URL])
    assert c._urls[0] == WIKIPEDIA_URL
    c = Entity('Nasir Jones', url=[URL, WIKIPEDIA])
    assert c.name_with_link == Text.from_markup(f'[link={URL}][bold underline]Nasir Jones[/bold underline][/link]')


def _build_contact(**kwargs) -> Entity:
    return Entity(NAME, **kwargs)
