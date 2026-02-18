from rich.text import Text

from epstein_files.output.highlight_config import CATEGORY_STYLES, HIGHLIGHT_GROUPS, get_style_for_category
from epstein_files.util.constants import *
from epstein_files.util.helpers.data_helpers import ALL_NAMES


def test_category_styles():
    """Check we didn't configure a style for a label/category twice."""
    for category in CATEGORY_STYLES:
        for highlight_group in HIGHLIGHT_GROUPS:
            assert highlight_group.label != category


def test_each_name_matches_only_one_highlight():
    for name in ALL_NAMES:
        if '(' in name or name == YUKO_BARNABY:  # TODO: fix this
            continue

        groups = [hg for hg in HIGHLIGHT_GROUPS if hg.regex.search(name)]
        group_labels = [hg.label for hg in groups]
        assert len(group_labels) <= 1, f"'{name}' matched {len(group_labels)} highlight groups: {group_labels}"


def test_highlight_labels():
    labels: set[str] = set([])

    for highlight_group in HIGHLIGHT_GROUPS:
        assert highlight_group.label not in labels
        labels.add(highlight_group.label)


def test_styled_category():
    assert get_style_for_category('crypto') == 'orange1 bold'
