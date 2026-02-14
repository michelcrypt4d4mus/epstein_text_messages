import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from rich.text import Text

from epstein_files.documents.other_file import Metadata, OtherFile
from epstein_files.util.constant.strings import JSON
from epstein_files.output.rich import INFO_STYLE

DESCRIPTION = "JSON data containing preview info for links sent in a messaging app like iMessage"

TEXT_FIELDS = [
    'caption',
    'standard',
    'subtitle',
    'text',
    'title',
    'to',
]


@dataclass
class JsonFile(OtherFile):
    """File containing JSON data."""
    include_description_in_summary_panel: ClassVar[bool] = False
    strip_whitespace: ClassVar[bool] = False

    @property
    def category(self) -> str:
        return JSON

    @property
    def is_interesting(self):
        return False

    @property
    def info_txt(self) -> Text | None:
        return Text(DESCRIPTION, style=INFO_STYLE)

    @property
    def metadata(self) -> Metadata:
        metadata = super().metadata
        metadata['description'] = DESCRIPTION
        return metadata

    def __post_init__(self):
        super().__post_init__()

        if self.url_slug.endswith('.txt') or self.url_slug.endswith('.json'):
            self.url_slug = Path(self.url_slug).stem

        self._set_computed_fields(text=self.json_str())

    def json_data(self) -> object:
        with open(self.file_path, encoding='utf-8-sig') as f:
            return json.load(f)

    def json_str(self) -> str:
        return json.dumps(self.json_data(), indent=4)
