import pytest

from epstein_files.util.constant.names import SULTAN_BIN_SULAYEM
from epstein_files.person import Person


@pytest.fixture(scope='session')
def sultan(epstein_files) -> Person:
    return epstein_files.person_objs([SULTAN_BIN_SULAYEM])[0]


def test_info_str(sultan):
    assert sultan.highlight_group() is not None
    assert sultan.info_str() == 'mideast, CEO of DP World, chairman of ports in Dubai'
