from rich.text import Text

from epstein_files.output.rich import hyperlink_line

URL = 'https://foo.bar'


def test_create_hyperlinks():
    assert hyperlink_line('foobar') == Text('foobar')
    assert hyperlink_line(URL) == Text.from_markup(f"[link={URL}]{URL}[/link]")
    assert hyperlink_line(f"> {URL} blah") == Text('> ').append(Text.from_markup(f"[link={URL}]{URL}[/link]")).append(' blah')
