from epstein_files.output.html.html_style import HtmlStyle

BRIGHT_RED = 'bright_red'
RED_RGB = '#ff0000'


def test_hex():
    no_style = HtmlStyle(None)
    assert no_style.foreground_color_hex == no_style.background_color_hex == ''

    red = HtmlStyle(BRIGHT_RED)
    assert red.foreground_color_hex == RED_RGB
    assert red.background_color_hex == ''

    on_red = HtmlStyle(f'on {BRIGHT_RED}')
    assert on_red.foreground_color_hex == ''
    assert on_red.background_color_hex == RED_RGB

    red_reverse = HtmlStyle(f'{BRIGHT_RED} reverse')
    # print(f"\n\nstyle: {red_reverse.style}\n    -> hex='{red_reverse.hex}'\n    -> bg_hex='{red_reverse.bg_hex}'\n    reverse: {red_reverse.style.reverse}")
    assert red_reverse.foreground_color_hex == ''
    assert red_reverse.background_color_hex == RED_RGB

    dim = HtmlStyle('dim')
    assert dim.foreground_color_hex == '#c0c0c0'
    assert dim.background_color_hex == ''
