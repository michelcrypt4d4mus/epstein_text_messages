from rich.text import Text

from epstein_files.output.rich import create_hyperlinks

URL = 'https://foo.bar'


def test_create_hyperlinks():
    assert create_hyperlinks('foobar') == Text('foobar')
    assert create_hyperlinks(URL) == Text.from_markup(f"[link={URL}]{URL}[/link]")
    assert create_hyperlinks(f"> {URL} blah") == Text('> ').append(Text.from_markup(f"[link={URL}]{URL}[/link]")).append(' blah')
