from epstein_files.util.helpers.data_helpers import *

NESTED_LIST = [[1, 2], [2, 3]]
NESTED_SETS = [set(e) for e in NESTED_LIST]


def test_flatten():
    assert flatten(NESTED_LIST) == [1, 2, 2, 3]
    assert flatten(NESTED_SETS) == [1, 2, 3]
