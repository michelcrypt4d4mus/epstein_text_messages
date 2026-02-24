from epstein_files.output.html.elements import *


def test_pre_code_console_template():
    assert pre_code_console_template() == """<pre style="font-family: Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><code style="font-family: inherit">{code}</code></pre>"""

def test_in_padded_div():
    pass
