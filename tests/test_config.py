from epstein_files.util.constants import *
from epstein_files.util.highlighted_group import CATEGORY_STYLES, HIGHLIGHTED_NAMES, ALL_HIGHLIGHTS


def test_other_files_config():
    encountered_file_ids = set()

    for cfg in ALL_CONFIGS:
        if cfg.duplicate_of_id:
            assert cfg.duplicate_of_id != cfg.id

        assert cfg.id not in encountered_file_ids
        encountered_file_ids.add(cfg.id)


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
