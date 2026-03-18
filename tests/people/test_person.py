import pytest

from epstein_files.people.person import Person
from epstein_files.people.names import *
from epstein_files.util.constant.strings import QUESTION_MARKS

SULAYEM_DESCRIPTION = 'chairman of ports in Dubai, CEO of DP World, resigned over Epstein ties'


@pytest.fixture(scope='session')
def sultan(epstein_files) -> Person:
    return epstein_files.person_objs([SULTAN_BIN_SULAYEM])[0]


@pytest.fixture(scope='session')
def john_page(epstein_files) -> Person:
    return epstein_files.person_objs([JOHN_PAGE])[0]


@pytest.fixture(scope='session')
def anne_boyles(epstein_files) -> Person:
    return epstein_files.person_objs(['Anne Boyles'])[0]


@pytest.fixture(scope='session')
def eva(epstein_files) -> Person:
    return epstein_files.person_objs([EVA_DUBIN])[0]


def test_info_str(anne_boyles, john_page, sultan):
    assert sultan.highlight_group is not None
    assert sultan.info_str == SULAYEM_DESCRIPTION
    assert sultan.info_with_category == f'mideast, {SULAYEM_DESCRIPTION}'

    assert john_page.highlight_group is None
    assert john_page.info_with_category == ''
    assert john_page.info_str is None

    assert anne_boyles.category_txt.plain == QUESTION_MARKS
    assert anne_boyles.info_txt.plain == QUESTION_MARKS
