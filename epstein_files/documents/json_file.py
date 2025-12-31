from dataclasses import dataclass
from pathlib import Path

from rich.text import Text

from epstein_files.documents.other_file import OtherFile


@dataclass
class JsonFile(OtherFile):
    """File containing JSON data."""

    def __post_init__(self):
        super().__post_init__()

        if self.url_slug.endswith('.txt') or self.url_slug.endswith('.json'):
            self.url_slug = Path(self.url_slug).stem

    def info_txt(self) -> Text | None:
        return Text(f"JSON data, possibly iMessage or similar app metadata", style='white dim italic')

    def is_interesting(self):
        return False
