from epstein_files.output.html.elements import *
from epstein_files.output.html.positioned_rich import *

HORIZONTAL_SIDES: list[Side] = ['left', 'right']
VERTICAL_SIDES: list[Side] = ['top', 'bottom']
CODE_TEMPLATE_TEST = """<code style="font-family: inherit">{code}</code>"""
PRE_TEMPLATE_TEST = f"""<pre>{CODE_TEMPLATE_TEST}</pre>"""


def test_dimensions_to_padding_css():
    assert dimensions_to_padding_css(1) == {f'padding-{side}': '1em' for side in SIDES}
    assert dimensions_to_padding_css((1,)) == {f'padding-{side}': '1em' for side in SIDES}
    assert dimensions_to_padding_css((1, 0)) == {f'padding-{side}': '1em' for side in VERTICAL_SIDES}
    assert dimensions_to_padding_css((0, 1)) == {f'padding-{side}': '1em' for side in HORIZONTAL_SIDES}

    assert dimensions_to_padding_css((1, 2)) == {
        **{f'padding-{side}': '2em' for side in HORIZONTAL_SIDES},
        **{f'padding-{side}': '1em' for side in VERTICAL_SIDES},
    }

    assert dimensions_to_padding_css((1, 2, 3, 4)) == {
        'padding-top': '1em',
        'padding-right': '2em',
        'padding-bottom': '3em',
        'padding-left': '4em',
    }


def test_pre_console_template():
    assert PRE_CONSOLE_TEMPLATE == """<pre>{code}</pre>-# JUNK #-{stylesheet} {background} {foreground}"""


def test_strip_tag():
    assert strip_outer_tag(CODE_TEMPLATE_TEST, 'code') == '{code}'
    assert strip_outer_tag(CODE_TEMPLATE_TEST, 'pre') == CODE_TEMPLATE_TEST
    assert strip_outer_tag(PRE_TEMPLATE_TEST, 'pre') == CODE_TEMPLATE_TEST


def test_tag():
    assert tag('div', 'foo', {}, role='cell') == '<div role="cell">foo</div>'
    assert tag('div', 'foo', {'width': '100px'}, class_name='cell') == '<div style="width: 100px" class="cell">foo</div>'
    assert tag('div', 'foo', FONT_CSS_PROPS) == """<div style="font-family: Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">foo</div>"""
