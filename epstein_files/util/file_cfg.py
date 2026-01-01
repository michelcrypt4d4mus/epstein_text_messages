from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from epstein_files.util.constant.names import constantize_name

ConfiguredAttr = Literal['actual_text', 'author', 'is_fwded_article', 'recipients', 'timestamp']
DuplicateType = Literal['same', 'earlier', 'quoted', 'redacted']

INDENT = '\n    '
INDENTED_JOIN = f',{INDENT}'
CONSTANTIZE_NAMES = True  # A flag set to True that causes repr() of these classes to return strings of usable code

REASON_MAPPING: dict[DuplicateType, str] = {
    'earlier': 'earlier draft of',
    'quoted': 'quoted in full in',
    'redacted': 'redacted version of',
    'same': 'the same as',
}


@dataclass(kw_only=True)
class FileCfg:
    """Convenience class that encapsulates configuring info about files that need to be manually configured.

    Attributes:
        id (str): ID of file
        duplicate_of_id (str | None): If this is a duplicate of another file, the ID of that file
        autduplicate_typehor (DuplicateType | None): The type of duplicate this file is
        timestamp (datetime | None): Time this email was sent, file was created, article published, etc.
    """
    id: str | None = None
    duplicate_of_id: str | None = None
    duplicate_type: DuplicateType | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.duplicate_of_id:
            self.duplicate_type = self.duplicate_type or 'same'

    def duplicate_reason(self) -> str | None:
        if self.duplicate_type is not None:
            return REASON_MAPPING[self.duplicate_type]

    def _props_strs(self) -> list[str]:
        props = []

        if self.id:
            props.append(f"id='{self.id}'")
        if self.duplicate_of_id:
            props.append(f"duplicate_of_id='{self.duplicate_of_id}'")
        if self.duplicate_type:
            props.append(f"duplicate_type='{self.duplicate_type}'")
        if self.timestamp:
            timestamp_str = f"parse('{self.timestamp}')" if CONSTANTIZE_NAMES else f"'{self.timestamp}'"
            props.append(f"timestamp={timestamp_str}")

        return props

    def __repr__(self) -> str:
        props = self._props_strs()
        type_str = f"{type(self).__name__}("
        single_line_repr = type_str + ', '.join(props) + f')'

        if len(single_line_repr) < 100:
            return single_line_repr
        else:
            return f"{type_str}{INDENT}" + INDENTED_JOIN.join(props) + f'\n)'


@dataclass(kw_only=True)
class EmailCfg(FileCfg):
    """
    Convenience class to unite various configured properties for a given email ID. Often required
    to handle the terrible OCR text that Congress provided which breaks a lot of the email's header lines.

    Attributes:
        actual_text (str | None): In dire cases of broken OCR we just configure the body of the email as a string.
        attribution_explanation (str | None): Optional explanation of why this email was attributed to this author.
        author (str | None): Author of the email
        is_fwded_article (bool): True if this is a newspaper article someone fwded. Used to exclude articles from word counting.
        recipients (list[str | None]): Who received the email
    """
    actual_text: str | None = None  # Override for the Email._actual_text() method for particularly broken emails
    attribution_explanation: str | None = None
    author: str | None = None
    is_fwded_article: bool = False
    recipients: list[str | None] | list[str] = field(default_factory=list)

    def _props_strs(self) -> list[str]:
        props = super()._props_strs()

        if self.author:
            author = constantize_name(self.author) if CONSTANTIZE_NAMES else self.author
            author = author if CONSTANTIZE_NAMES else f"'{author}'"
            props.append(f"author={author}")
        if self.recipients:
            recipients = [constantize_name(r) if (CONSTANTIZE_NAMES and r) else r for r in self.recipients]
            recipients_str = f"recipients={recipients}"

            if CONSTANTIZE_NAMES:
                recipients_str = recipients_str.replace("'", '')

            props.append(recipients_str)
        if self.is_fwded_article:
            props.append(f"is_fwded_article={self.is_fwded_article}")
        if self.actual_text:
            props.append(f"actual_text='{self.actual_text}'")

        return props

    def __repr__(self) -> str:
        return super().__repr__()
