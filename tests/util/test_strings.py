from epstein_files.util.constant.strings import indented


def test_indented():
    assert indented('buff') == '    buff'
    assert indented('buff\nillmatic') == '    buff\n    illmatic'
    assert indented('buff\nillmatic', prefix='> ') == '    > buff\n    > illmatic'
