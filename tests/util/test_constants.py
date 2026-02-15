from epstein_files.util.constants import CONFIGS_BY_ID


def test_no_overlapping_configs():
    encountered_file_ids = set()

    for cfg in CONFIGS_BY_ID.values():
        if cfg.duplicate_of_id:
            assert cfg.duplicate_of_id != cfg.id

        assert cfg.id not in encountered_file_ids
        encountered_file_ids.add(cfg.id)
