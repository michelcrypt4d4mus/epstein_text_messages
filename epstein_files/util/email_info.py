from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from epstein_files.util.constant.names import constantize_name

ConfiguredAttr = Literal['actual_text', 'author', 'is_fwded_article', 'recipients', 'timestamp']
DuplicateType = Literal['same as', 'earlier', 'quoted in', 'redacted version of']

COMMA_JOIN = ', '
INDENT = '\n    '
INDENTED_JOIN = f',{INDENT}'
CONSTANTIZE_NAMES = True


@dataclass(kw_only=True)
class FileConfig:
    id: str | None = None
    duplicate_of_id: str | None = None
    duplicate_type: DuplicateType | None = None

    # Housekeeping TODO: remove this
    _use_newline_join: bool = False

    def __post_init__(self):
        if self.duplicate_of_id:
            self.duplicate_type = self.duplicate_type or 'same as'

    def _props_strs(self) -> list[str]:
        props = []

        if self.id:
            props.append(f"file_id='{self.id}'")
        if self.duplicate_of_id:
            props.append(f"duplicate_of_id='{self.duplicate_of_id}'")
        if self.duplicate_type:
            props.append(f"duplicate_type='{self.duplicate_type}'")

        return props

    def _final_props_str(self, props: list[str]) -> str:
        joiner = INDENTED_JOIN if self._use_newline_join else COMMA_JOIN
        initial_char = INDENT if self._use_newline_join else ''
        final_char = '\n' if self._use_newline_join else ''
        return f"{type(self).__name__}({initial_char}" + joiner.join(props) + f'{final_char})'

    def __repr__(self) -> str:
        return self._final_props_str(self._props_strs())


@dataclass(kw_only=True)
class EmailConfig(FileConfig):
    """Convenience class to unite various configured properties for a given email ID."""
    actual_text: str | None = None  # Override for the Email._actual_text() method
    author: str | None = None
    is_fwded_article: bool = False
    recipients: list[str | None] | list[str] = field(default_factory=list)
    timestamp: datetime | None = None

    def __repr__(self) -> str:
        props = self._props_strs()

        if self.author:
            author = constantize_name(self.author) if CONSTANTIZE_NAMES else self.author
            author = author if CONSTANTIZE_NAMES else f"'{author}'"
            props.append(f"author={author}")
            self._use_newline_join = True
        if self.recipients:
            recipients = [constantize_name(r) if (CONSTANTIZE_NAMES and r) else r for r in self.recipients]
            recipients_str = f"recipients={recipients}"

            if CONSTANTIZE_NAMES:
                recipients_str = recipients_str.replace("'", '')

            props.append(recipients_str)
            self._use_newline_join = True
        if self.is_fwded_article:
            props.append(f"is_fwded_article={self.is_fwded_article}")
            self._use_newline_join = True
        if self.timestamp:
            timestamp_str = f"parse('{self.timestamp}')" if CONSTANTIZE_NAMES else f"'{self.timestamp}'"
            props.append(f"timestamp={timestamp_str}")
            self._use_newline_join = True
        if self.actual_text:
            props.append(f"actual_text='{self.actual_text}'")
            self._use_newline_join = True

        return self._final_props_str(props)
