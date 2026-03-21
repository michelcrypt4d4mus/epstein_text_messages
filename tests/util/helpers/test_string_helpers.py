from epstein_files.util.helpers.string_helper import doublespace_lists, as_pattern, extract_emojis, has_line_starting_with, indented

EMAIL_TEXT = ">From: umar ovk.ru\n>To:\n>Subject:"

NUMBERED_LIST = """
Lorem Ipsum ipsum dipsum
Lorem Ipsum ipsum dipsum
1. Solo no goes
2. Unmoving
3. Sorry
4. For All
5. the fish"""


def test_as_pattern():
    assert as_pattern('nas - illmatic') == r'nas[-_.\s]*-[-_.\s]*illmatic'
    assert as_pattern('nas     illmatic') == r"nas[-_.\s]*illmatic"


def test_doublespace_numbered_lists():
    assert doublespace_lists(NUMBERED_LIST) == """
Lorem Ipsum ipsum dipsum
Lorem Ipsum ipsum dipsum

1. Solo no goes

2. Unmoving

3. Sorry

4. For All

5. the fish"""


def test_extract_emojis():
    assert extract_emojis('thanks :)') == [':)']
    assert extract_emojis('thanks :-) see you') == [':-)']
    assert extract_emojis('thanks :-) see you :P\nhappy :) :D who (-:') == [':-)', ':P', ':)', ':D', '(-:']
    assert extract_emojis('(^: hoo boy') == ['(^:']
    assert extract_emojis(EMAIL_TEXT) == []


def test_indented():
    assert indented('buff') == '    buff'
    assert indented('buff\nillmatic') == '    buff\n    illmatic'
    assert indented('buff\nillmatic', prefix='> ') == '    > buff\n    > illmatic'
    assert indented(['buff', 'illmatic'], prefix='> ') == '    > buff\n    > illmatic'


def test_has_line_starting_with():
    assert has_line_starting_with('foobar\nillmat\nic', 'foo')
    assert has_line_starting_with('foobar\nillmat\nice', ['ill'])
    assert has_line_starting_with('foobar\nillmat\nice', ['ice'])
    assert has_line_starting_with('foobar\nillmat\nice', ['ice'], 2) is False
