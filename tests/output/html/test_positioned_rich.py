from rich.align import Align, AlignMethod
from rich.console import RenderableType
from rich.padding import Padding, PaddingDimensions
from rich.panel import Panel
from rich.text import Text

from epstein_files.output.html.positioned_rich import CENTERED, CssProps, PositionedRich

TEXT = text = Text('some text')


def test_from_unwrapped_obj():
    def _assert_unwrapped_css(obj: RenderableType, expected_css: CssProps):
        positioned = PositionedRich.from_unwrapped_obj(obj)
        assert positioned.obj == TEXT
        assert positioned.css == expected_css

    _assert_unwrapped_css(TEXT, {})
    aligned_text = Align(TEXT, 'center')
    _assert_unwrapped_css(aligned_text, CENTERED)
    padded_text = Padding(TEXT, (0, 0, 1, 0))
    _assert_unwrapped_css(padded_text, {'margin-bottom': '1em'})
    padded_aligned = Align(padded_text, 'center')
    _assert_unwrapped_css(padded_aligned, {'margin-bottom': '1em', **CENTERED})
    padded_aligned = Align(padded_text, 'left')
    _assert_unwrapped_css(padded_aligned, {'margin-bottom': '1em', 'margin-right': 'auto'})
    padded_aligned = Align(padded_text, 'right')
    _assert_unwrapped_css(padded_aligned, {'margin-bottom': '1em', 'margin-left': 'auto'})

    panel = Panel('Foo Bar', padding=(1, 1))
    positioned = PositionedRich.from_unwrapped_obj(panel)
    assert positioned.obj == panel
    assert positioned.css == {}  # Inner padding on a panel is not applied here, only enclsoing Padding/Aligns

    aligned_panel = Align.center(panel)
    positioned = PositionedRich.from_unwrapped_obj(aligned_panel)
    assert positioned.alignment_css == CENTERED
    assert positioned.css == CENTERED
    assert positioned.obj == panel

    padded_aligned_panel = Padding(aligned_panel, (2, 0, 1, 0))
    positioned = PositionedRich.from_unwrapped_obj(padded_aligned_panel)
    assert positioned.alignment_css == CENTERED
    assert positioned.css == {'margin-top': '2em', 'margin-bottom': '1em', **CENTERED}
    assert positioned.obj == panel
