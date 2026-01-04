import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from rich.text import Text

from epstein_files.documents.other_file import OtherFile
from epstein_files.util.rich import console


@dataclass
class JsonFile(OtherFile):
    """File containing JSON data."""
    strip_whitespace: ClassVar[bool] = False

    def __post_init__(self):
        super().__post_init__()

        if self.url_slug.endswith('.txt') or self.url_slug.endswith('.json'):
            self.url_slug = Path(self.url_slug).stem

        self._set_computed_fields(text=self.formatted_json())

    def category(self) -> str:
        return 'json'

    def formatted_json(self) -> str:
        return json.dumps(self.json_data(), indent=4)

    def info_txt(self) -> Text | None:
        return Text(f"JSON file, possibly iMessage or similar app metadata", style='white dim italic')

    def is_interesting(self):
        return False

    def json_data(self) -> object:
        with open(self.file_path, encoding='utf-8-sig') as f:
            return json.load(f)
