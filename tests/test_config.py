from epstein_files.util.constants import ALL_CONFIGS


def test_other_files_config():
    encountered_file_ids = set()

    for cfg in ALL_CONFIGS:
        if cfg.duplicate_of_id:
            assert cfg.duplicate_of_id != cfg.id

        assert cfg.id not in encountered_file_ids
        encountered_file_ids.add(cfg.id)
