import pytest

from epstein_files.person import Person
from epstein_files.util.constant.names import *


@pytest.fixture(scope='session')
def sultan(epstein_files) -> Person:
    return epstein_files.person_objs([SULTAN_BIN_SULAYEM])[0]


@pytest.fixture(scope='session')
def eduardo(epstein_files) -> Person:
    return epstein_files.person_objs([EDUARDO_ROBLES])[0]



def test_info_str(eduardo, sultan):
    assert sultan.highlight_group() is not None
    assert sultan.info_str() == 'CEO of DP World, chairman of ports in Dubai'
    assert sultan.info_with_category() == 'mideast, CEO of DP World, chairman of ports in Dubai'

    assert eduardo.highlight_group() is None
    assert eduardo.info_with_category() == ''
    assert eduardo.info_str() is None
