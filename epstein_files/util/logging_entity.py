import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from epstein_files.util.logging import logger


class LoggingEntity(ABC):
    """Classes that implement a `_log_prefix()` method can call self._log(), self._warn(), etc."""

    @property
    @abstractmethod
    def _log_prefix(self) -> str:
        pass

    def _debug_log(self, msg: str) -> None:
        self._log(msg, logging.DEBUG)

    def _warn(self, msg: str) -> None:
        self._log(msg, logging.WARNING)

    def _log(self, msg: str, level: int = logging.INFO) -> None:
        logger.log(level, f"{self._log_prefix} {msg}")
