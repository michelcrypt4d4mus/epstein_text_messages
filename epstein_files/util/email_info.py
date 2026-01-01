from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

ConfiguredAttr = Literal['actual_text', 'author', 'is_fwded_article', 'recipients', 'timestamp']


@dataclass(kw_only=True)
class FileConfig:
    file_id: str | None = None
    duplicate_of_file_id: str | None = None
    duplicate_type: Literal['same', 'redacted version'] | None = None

    def __post_init__(self):
        if self.duplicate_of_file_id:
            self.duplicate_type = self.duplicate_type or 'same'


@dataclass(kw_only=True)
class EmailConfig(FileConfig):
    """Convenience class to unite various configured properties for a given email ID."""
    actual_text: str | None = None  # Override for the Email._actual_text() method
    author: str | None = None
    is_fwded_article: bool = False
    recipients: list[str | None] | list[str] = field(default_factory=list)
    timestamp: datetime | None = None

    def __repr__(self) -> str:
        props = []

        if self.author:
            props.append(f"author='{self.author}'")
        if self.is_fwded_article:
            props.append(f"is_fwded_article={self.is_fwded_article}")
        if self.recipients:
            props.append(f"recipients={self.recipients}")
        if self.timestamp:
            props.append(f"timestamp='{self.timestamp}'")
        if self.actual_text:
            props.append(f"actual_text='{self.actual_text}'")

        return f"{type(self).__name__}({', '.join(props)})"
