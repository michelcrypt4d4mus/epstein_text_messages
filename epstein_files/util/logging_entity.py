import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from epstein_files.util.logging import logger


class LoggingEntity(ABC):
    """
    Classes that implement `_identifier()` or overload `_log_prefix()` can call self._log(), self._warn(), etc.
    """

    @property
    def _class_name(self) -> str:
        return type(self).__name__

    @property
    @abstractmethod
    def _identifier(self) -> str:
        """Overload for a reusable approach to  _log_prefix, e.g. Document(12345) or Person('James')"""
        pass

    @property
    def _log_prefix(self) -> str:
        return f"{self._class_name}({self._identifier})"

    def _debug_log(self, msg: str) -> None:
        self._log(msg, logging.DEBUG)

    def _error(self, msg: str) -> None:
        self._log(msg, logging.ERROR)

    def _log(self, msg: str, level: int = logging.INFO) -> None:
        logger.log(level, f"{self._log_prefix} {msg}")

    def _warn(self, msg: str) -> None:
        self._log(msg, logging.WARNING)
