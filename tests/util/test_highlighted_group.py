from rich.text import Text

from epstein_files.util.constants import *
from epstein_files.util.helpers.data_helpers import ALL_NAMES
from epstein_files.util.highlighted_group import CATEGORY_STYLES, HIGHLIGHTED_NAMES, get_style_for_category


def test_category_styles():
    """Check we didn't configure a style for a label/category twice."""
    for category in CATEGORY_STYLES:
        for highlight_group in HIGHLIGHTED_NAMES:
            assert highlight_group.label != category


def test_highlight_labels():
    labels: set[str] = set([])

    for highlight_group in HIGHLIGHTED_NAMES:
        assert highlight_group.label not in labels
        labels.add(highlight_group.label)


def test_each_name_matches_only_one_highlight():
    for name in ALL_NAMES:
        if '(' in name:
            continue

        highlight_groups = [hg for hg in HIGHLIGHTED_NAMES if hg.regex.search(name)]
        assert len(highlight_groups) <= 1, f"'{name}' matched {len(highlight_groups)} highlight groups!"


def test_styled_category():
    assert get_style_for_category('crypto') == 'orange1 bold'
