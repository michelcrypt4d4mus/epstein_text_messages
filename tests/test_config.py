from epstein_files.util.constants import *


def test_other_files_config():
    assert len(OTHER_FILES_CONFIG) == 443
    encountered_file_ids = set()

    for cfg in ALL_CONFIGS:
        if cfg.dupe_of_id:
            assert cfg.dupe_of_id != cfg.id

        assert cfg.id not in encountered_file_ids
        encountered_file_ids.add(cfg.id)
