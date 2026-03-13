from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel
from rich.text import Text

from epstein_files.output.html.builder import unwrap_rich
from epstein_files.output.html.elements import CENTERED


def test_unwrap_rich():
    text = Text('some text')
    assert unwrap_rich(text) == (text, {})
    aligned_text = Align(text, 'center')
    assert unwrap_rich(aligned_text) == (text, CENTERED)
    padded_text = Padding(text, (0, 0, 1, 0))
    assert unwrap_rich(padded_text) == (text, {'margin-bottom': '1em'})
    padded_aligned = Align(padded_text, 'center')
    assert unwrap_rich(padded_aligned) == (text, {'margin-bottom': '1em', **CENTERED})
    padded_aligned = Align(padded_text, 'left')
    assert unwrap_rich(padded_aligned) == (text, {'margin-bottom': '1em', 'margin-right': 'auto'})
    padded_aligned = Align(padded_text, 'right')
    assert unwrap_rich(padded_aligned) == (text, {'margin-bottom': '1em', 'margin-left': 'auto'})

    panel = Panel('Foo Bar', padding=(1, 1))
    assert unwrap_rich(panel) == (panel, {})
    aligned_panel = Align.center(panel)
    assert unwrap_rich(aligned_panel) == (panel, CENTERED)
    padded_aligned_panel = Padding(aligned_panel, (2, 0, 2, 0))
    assert unwrap_rich(padded_aligned_panel) == (panel, {'margin-top': '2em', 'margin-bottom': '2em', **CENTERED})
