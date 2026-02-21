import json
from dataclasses import dataclass
from typing import ClassVar

from rich.text import Text

from epstein_files.documents.other_file import Metadata, OtherFile
from epstein_files.output.rich import INFO_STYLE
from epstein_files.util.constant.strings import JSON

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
    INCLUDE_DESCRIPTION_IN_SUMMARY_PANEL: ClassVar[bool] = False
    STRIP_WHITESPACE: ClassVar[bool] = False

    def __post_init__(self):
        super().__post_init__()
        self._set_text(text=self.json_str())

    @property
    def category(self) -> str:
        return JSON

    @property
    def is_interesting(self):
        return False

    @property
    def metadata(self) -> Metadata:
        metadata = super().metadata
        metadata['description'] = DESCRIPTION
        return metadata

    @property
    def subheader(self) -> Text:
        return Text(DESCRIPTION, style=INFO_STYLE)

    def json_data(self) -> object:
        with open(self.file_path, encoding='utf-8-sig') as f:
            return json.load(f)

    def json_str(self) -> str:
        return json.dumps(self.json_data(), indent=4)
