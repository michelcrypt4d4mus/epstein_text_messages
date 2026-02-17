from epstein_files.documents.documents.categories import *
from epstein_files.util import constants


def test_is_interesting():
    assert is_interesting('crypto')
    assert not is_interesting('phone_bill')


def test_var_name_categories():
    other_files_consts = [v for v in dir(constants) if v.startswith('OTHER_FILES_') and not v.endswith('PFX')]

    for const in other_files_consts:
        assert is_category(const.removeprefix(constants.OTHER_FILES_PFX).lower())
