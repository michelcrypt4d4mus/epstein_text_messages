import time
from dataclasses import dataclass, field

from epstein_files.util.logging import logger


@dataclass
class Timer:
    started_at: float = field(default_factory=lambda: time.perf_counter())
    checkpoint_at: float = field(default_factory=lambda: time.perf_counter())
    decimals: int = 2

    def print_at_checkpoint(self, msg: str) -> None:
        logger.warning(f"{msg} in {self.seconds_since_checkpoint_str()}...")
        self.checkpoint_at = time.perf_counter()

    def seconds_since_checkpoint_str(self) -> str:
        return f"{(time.perf_counter() - self.checkpoint_at):.{self.decimals}f} seconds"

    def seconds_since_start(self) -> float:
        return time.perf_counter() - self.started_at

    def seconds_since_start_str(self) -> str:
        return f"{self.seconds_since_start():.{self.decimals}f} seconds"
