from datetime import datetime

from epstein_files.util.helpers.data_helpers import *

NESTED_LIST = [[1, 2], [2, 3]]
NESTED_SETS = [set(e) for e in NESTED_LIST]


def test_days_between():
    dt1 = datetime.fromisoformat('2006-01-01T00:00:00+00:00')
    dt2 = datetime.fromisoformat('2005-03-16T00:00:00+00:00')
    assert days_between(dt1, dt2) == -290
    assert days_between(dt2, dt1) == 292
    assert days_between_abs(dt1, dt2) == 290


def test_flatten():
    assert flatten(NESTED_LIST) == [1, 2, 2, 3]
    assert flatten(NESTED_SETS) == [1, 2, 3]
