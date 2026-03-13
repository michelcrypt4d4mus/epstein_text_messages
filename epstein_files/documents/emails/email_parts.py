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

    @property
    def header_txt(self) -> Text:
        return highlighter(self.header)
