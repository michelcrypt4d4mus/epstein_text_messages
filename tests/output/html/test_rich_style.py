from epstein_files.output.html.rich_style import RichStyle

BRIGHT_RED = 'bright_red'
RED_RGB = '#ff0000'


def test_hex():
    no_style = RichStyle(None)
    assert no_style.foreground_color_hex == no_style.background_color_hex == ''

    red = RichStyle(BRIGHT_RED)
    assert red.foreground_color_hex == RED_RGB
    assert red.background_color_hex == ''

    on_red = RichStyle(f'on {BRIGHT_RED}')
    assert on_red.foreground_color_hex == ''
    assert on_red.background_color_hex == RED_RGB

    red_reverse = RichStyle(f'{BRIGHT_RED} reverse')
    # print(f"\n\nstyle: {red_reverse.style}\n    -> hex='{red_reverse.hex}'\n    -> bg_hex='{red_reverse.bg_hex}'\n    reverse: {red_reverse.style.reverse}")
    assert red_reverse.foreground_color_hex == ''
    assert red_reverse.background_color_hex == RED_RGB

    dim = RichStyle('dim')
    assert dim.foreground_color_hex == '#c0c0c0'
    assert dim.background_color_hex == ''
