"""Helpers for dealing with environment variables."""
from os import environ
from pathlib import Path

from epstein_files.util.logging import exit_with_error, logger


def get_env_dir(env_var_name: str, must_exist: bool = True) -> Path | None:
    if (dir := environ.get(env_var_name)):
        dir = Path(dir)
        error_msg = f"env var {env_var_name} set to '{dir}' but that's not a directory"

        if dir.is_dir():
            return dir.resolve()
        elif must_exist:
            exit_with_error(f"Required {error_msg}.\n")
        else:
            logger.warning(f"Optional {error_msg}. Some features will be unavailable.")
            return None
    else:
        logger.warning(f"Optional env var {env_var_name} not set. Some features will be unavailable.")
