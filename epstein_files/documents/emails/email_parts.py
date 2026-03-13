import json
import re
from dataclasses import asdict, dataclass, field

from rich.text import Text

from epstein_files.output.epstein_highlighter import highlighter


@dataclass
class EmailParts:
    """Simple container to hold the header and body strings for an email in separate variables."""
    header: str
    body: str

    def __post_init__(self):
        self.header = self.header.strip()
        self.body = self.body.strip()

    @property
    def header_txt(self) -> Text:
        return highlighter(self.header)

    @property
    def header_len(self) -> int:
        return len(self.header)

    def __str__(self) -> str:
        return f"{self.header}\n\n{self.body}"
