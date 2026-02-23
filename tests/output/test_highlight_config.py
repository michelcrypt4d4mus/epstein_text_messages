from pathlib import Path

HIGHLIGHT_CONFIG_PY = Path(__file__).parent.parent.parent.joinpath('epstein_files', 'output', 'highlight_config.py')


def test_no_missing_commas():
    for line in [ln for ln in HIGHLIGHT_CONFIG_PY.read_text().split('\n') if ln.startswith('            r"')]:
        if '#' in line:
            line = line.split('#')[0].rstrip()

        assert line.endswith(','), f"{line} should end with a comma"
