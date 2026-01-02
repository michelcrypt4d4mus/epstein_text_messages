import re
from dataclasses import Field, asdict, dataclass, field, fields
from datetime import datetime
from typing import Literal

from epstein_files.util.constant.names import constantize_name
from epstein_files.util.constant.strings import AUTHOR

ConfiguredAttr = Literal['actual_text', 'author', 'is_fwded_article', 'recipients', 'timestamp']
DuplicateType = Literal['same', 'earlier', 'quoted', 'redacted']

INDENT = '    '
INDENT_NEWLINE = f'\n{INDENT}'
INDENTED_JOIN = f',{INDENT_NEWLINE}'
CONSTANTIZE_NAMES = True  # A flag set to True that causes repr() of these classes to return strings of usable code
MAX_LINE_LENGTH = 120

REASON_MAPPING: dict[DuplicateType, str] = {
    'earlier': 'earlier draft of',
    'quoted': 'quoted in full in',
    'redacted': 'redacted version of',
    'same': 'the same as',
}

FIELD_SORT_KEY = {
    'id': 'a',
    'author': 'aa',
    'attribution_explanation': 'zz',
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
    description: str | None = None
    duplicate_of_id: str | None = None
    duplicate_type: DuplicateType | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.duplicate_of_id:
            self.duplicate_type = self.duplicate_type or 'same'

    def duplicate_reason(self) -> str | None:
        if self.duplicate_type is not None:
            return REASON_MAPPING[self.duplicate_type]

    def non_null_field_names(self) -> list[str]:
        return [f.name for f in self.sorted_fields() if getattr(self, f.name)]

    def sorted_fields(self) -> list[Field]:
        return sorted(fields(self), key=lambda f: FIELD_SORT_KEY.get(f.name, f.name))

    def _props_strs(self) -> list[str]:
        props = []

        def add_prop(f: Field, value: str):
            props.append(f"{f.name}={value}")

        for _field in self.sorted_fields():
            value = getattr(self, _field.name)

            if value is None or (isinstance(value, list) and len(value) == 0):
                continue
            elif isinstance(value, bool) and not value:
                continue
            elif _field.name == AUTHOR:
                add_prop(_field, constantize_name(str(value)) if CONSTANTIZE_NAMES else f"'{value}'")
            elif _field.name == 'recipients' and isinstance(value, list):
                recipients_str = str([constantize_name(r) if (CONSTANTIZE_NAMES and r) else r for r in value])
                add_prop(_field, recipients_str.replace("'", '') if CONSTANTIZE_NAMES else recipients_str)
            elif isinstance(value, datetime):
                value_str = re.sub(' 00:00:00', '', str(value))
                add_prop(_field, f"parse('{value_str}')" if CONSTANTIZE_NAMES else f"'{value}'")
            elif _field.name == 'description':
                add_prop(_field, value.strip())
#                add_prop(_field, value.replace('",', '"').replace("',", "'").strip())
            elif isinstance(value, str):
                if "'" in value:
                    value = '"' + value.replace('"', r'\"') + '"'
                else:
                    value = "'" + value.replace("'", r'\'') + "'"

                add_prop(_field, value)
            else:
                add_prop(_field, str(value))

        return props

    def __repr__(self) -> str:
        props = self._props_strs()
        type_str = f"{type(self).__name__}("
        single_line_repr = type_str + ', '.join(props) + f')'

        if (len(single_line_repr) < MAX_LINE_LENGTH or self.non_null_field_names() == ['id', 'description']) and '#' not in (self.description or ''):
            repr_str = single_line_repr
        else:
            repr_str = f"{type_str}{INDENT_NEWLINE}" + INDENTED_JOIN.join(props)
            repr_str += ',' if props else ''
            repr_str += '\n)'

        if CONSTANTIZE_NAMES:
            repr_str = INDENT + INDENT_NEWLINE.join(repr_str.split('\n'))

        return repr_str.replace(',,', ',').replace(',),', '),').replace(',),', '),')


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
    is_attribution_uncertain: bool = False
    is_fwded_article: bool = False
    recipients: list[str | None] = field(default_factory=list)

    def __repr__(self) -> str:
        return super().__repr__()

    @classmethod
    def from_file_cfg(cls, cfg: FileCfg) -> 'EmailCfg':
        return cls(**asdict(cfg))
