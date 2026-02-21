from epstein_files.util.helpers.string_helper import as_pattern, has_line_starting_with, indented


def test_as_pattern():
    assert as_pattern('nas - illmatic') == r'nas[-_\s]*-[-_\s]*illmatic'
    assert as_pattern('nas     illmatic') == r"nas[-_\s]*illmatic"


def test_indented():
    assert indented('buff') == '    buff'
    assert indented('buff\nillmatic') == '    buff\n    illmatic'
    assert indented('buff\nillmatic', prefix='> ') == '    > buff\n    > illmatic'


def test_has_line_starting_with():
    assert has_line_starting_with('foobar\nillmat\nic', 'foo')
    assert has_line_starting_with('foobar\nillmat\nice', ['ill'])
    assert has_line_starting_with('foobar\nillmat\nice', ['ice'])
    assert has_line_starting_with('foobar\nillmat\nice', ['ice'], 2) is False
