from epstein_files.output.html.html_style import HtmlStyle

BRIGHT_RED = 'bright_red'
RED_RGB = '#ff0000'


def test_hex():
    no_style = HtmlStyle(None)
    assert no_style.hex == no_style.bg_hex == ''

    red = HtmlStyle(BRIGHT_RED)
    assert red.hex == RED_RGB
    assert red.bg_hex == ''

    on_red = HtmlStyle(f'on {BRIGHT_RED}')
    assert on_red.hex == ''
    assert on_red.bg_hex == RED_RGB

    red_reverse = HtmlStyle(f'{BRIGHT_RED} reverse')
    # print(f"\n\nstyle: {red_reverse.style}\n    -> hex='{red_reverse.hex}'\n    -> bg_hex='{red_reverse.bg_hex}'\n    reverse: {red_reverse.style.reverse}")
    assert red_reverse.hex == ''
    assert red_reverse.bg_hex == RED_RGB
