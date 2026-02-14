import time
from dataclasses import dataclass, field
from typing import Type

from epstein_files.util.logging import logger


@dataclass
class Timer:
    started_at: float = field(default_factory=lambda: time.perf_counter())
    checkpoint_at: float = field(default_factory=lambda: time.perf_counter())
    decimals: int = 2

    def log_section_complete(self, label: str, all_docs: list, printed_docs: list) -> None:
        num_skipped = len(all_docs) - len(printed_docs)
        prefix = suffix = ''

        if num_skipped == 0:
            prefix = 'all '
        elif num_skipped < 0:
            suffix = f"(at least {-1 * num_skipped} {label}s printed more than once)"
        else:
            suffix = f"(skipped {num_skipped})"

        self.print_at_checkpoint(f"Printed {prefix}{len(printed_docs)} {label}s {suffix}".strip())

    def print_at_checkpoint(self, msg: str) -> None:
        logger.warning(f"{msg} in {self.seconds_since_checkpoint_str()}...")
        self.checkpoint_at = time.perf_counter()

    def seconds_since_checkpoint_str(self) -> str:
        return f"{(time.perf_counter() - self.checkpoint_at):.{self.decimals}f} seconds"

    def seconds_since_start(self) -> float:
        return time.perf_counter() - self.started_at

    def seconds_since_start_str(self) -> str:
        return f"{self.seconds_since_start():.{self.decimals}f} seconds"
